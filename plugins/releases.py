#!/usr/bin/python -tt
##
# Copyright (C) 2013 by Kernel.org
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
import os
import time
import datetime
import re

from git import Repo

from pelican import signals, utils

from feedgenerator import Rss201rev2Feed
import json


# Pelican plugin API
def register():
    signals.article_generator_init.connect(kernel_releases_init)
    signals.article_generate_context.connect(fetch_kernel_releases)


def kernel_releases_init(gen):
    gen.releases_instance = KernelReleases(gen)


def fetch_kernel_releases(gen, metadata):
    gen.context['current_releases'] = gen.releases_instance.current_releases
    gen.context['latest_release'] = gen.releases_instance.latest_release


class KernelReleases():
    def __init__(self, generator):
        self.release_tracker = '/var/lib/mirror/release-tracker.json'

        self.rss_path = os.path.join(generator.output_path, 'feeds', 'kdist.xml')
        self.finger_path = os.path.join(generator.output_path, 'finger_banner')
        self.json_path = os.path.join(generator.output_path, 'releases.json')

        settings = generator.settings

        GIT_MAINLINE = settings.get('GIT_MAINLINE')
        GIT_STABLE = settings.get('GIT_STABLE')
        GIT_NEXT = settings.get('GIT_NEXT')

        LONGTERM_KERNELS = settings.get('LONGTERM_KERNELS')
        EOL_KERNELS = settings.get('EOL_KERNELS')

        self.pub_mount = settings.get('PUB_MOUNT')

        repo = Repo(GIT_MAINLINE)
        tagrefs = self.get_tagref_list(repo)

        rc_reg = re.compile('v.*-rc\d+$')
        mainline_rc = self.find_latest_matching(tagrefs, rc_reg)
        rel_reg = re.compile('v[^-]*\d+$')
        mainline_rel = self.find_latest_matching(tagrefs, rel_reg)

        # if mainline_rel is newer than mainline_rc, ignore mainline_rc
        if mainline_rc[1] < mainline_rel[1]:
            mainline_rc = None

        # Move on to the linux-stable repo
        repo = Repo(GIT_STABLE)
        # ignore any tags older than 12 months
        cutoff = time.time() - 31536000

        # EOL cutoff is 30 days
        eol_cutoff = time.time() - 2592000

        tagrefs = self.get_tagref_list(repo, cutoff)

        # find all tags matching vX.X.X
        rel_reg = re.compile('v\d+\.\d+\.\d+$')
        matched = []
        for tagref in tagrefs:
            if rel_reg.match(tagref.name):
                matched.append(tagref)

        stable = []
        seen = []

        for tagref in matched:
            # does it match a longterm release?
            ignore = False
            for ver in LONGTERM_KERNELS:
                if tagref.name.find(ver) == 1:
                    # this is a long-term release, ignore
                    ignore = True
                    continue
            if ignore:
                continue

            # Drop the final \.\d+ and find the latest matching
            components = tagref.name.split('.')
            regex = re.compile('^' + '\\.'.join(components[:-1]))

            if regex in seen:
                continue

            latest_matching = self.find_latest_matching(matched, regex)
            if latest_matching is not None:
                stable.append(latest_matching)

            seen.append(regex)

        stable = sorted(stable, key=lambda tagged: int(tagged[0].split('.')[1]), reverse=True)

        releases = []

        if mainline_rc is not None:
            releases.append(self.make_release_line(mainline_rc, 'mainline'))

        # look at the last stable and see if mainline_rel fits into it
        latest_stable = stable.pop(0)

        if latest_stable[0].find(mainline_rel[0]) != 0:
            releases.append(self.make_release_line(mainline_rel, 'mainline'))
            latest = self.make_release_line(mainline_rel, 'latest')
        else:
            latest = self.make_release_line(latest_stable, 'latest')
            # if latest stable is newer than latest mainline, but there are no
            # -rc kernels, list the latest mainline in the releases table anyway.
            if mainline_rc is None:
                releases.append(self.make_release_line(mainline_rel, 'mainline'))

        releases.append(self.make_release_line(latest_stable, 'stable'))

        # add other stable kernels and mark EOL accordingly
        for rel in stable:
            iseol = False
            for eolrel in EOL_KERNELS:
                if rel[0].find(eolrel) == 1:
                    iseol = True
                    break

            # Make sure EOL kernels stick around for max 30 days
            if iseol and rel[1] < eol_cutoff:
                continue

            releases.append(self.make_release_line(rel, 'stable', iseol))

        # find latest long-term releases
        for rel in LONGTERM_KERNELS:
            components = rel.split('.')
            regex = re.compile('^v' + '\\.'.join(components) + '\\.\\d+$')
            found = self.find_latest_matching(tagrefs, regex)
            if found is not None:
                iseol = False
                for eolrel in EOL_KERNELS:
                    if found[0].find(eolrel) == 1:
                        iseol = True
                        break

                if iseol and found[1] < eol_cutoff:
                    # Too old to list on the front page
                    continue

                releases.append(self.make_release_line(found, 'longterm', iseol))

        # now find latest tag in linux-next
        repo = Repo(GIT_NEXT)
        tagrefs = self.get_tagref_list(repo, cutoff)

        regex = re.compile('^next-')
        rel = self.find_latest_matching(tagrefs, regex)
        releases.append(self.make_release_line(rel, 'linux-next'))

        self.current_releases = releases
        self.latest_release = latest

        self.generate_rss_feed()
        self.generate_finger_banner()
        self.generate_releases_json()
        self.check_release_tracker()

    def check_release_tracker(self):
        if 'PELICAN_DRYRUN' in os.environ.keys():
            return

        import socket
        send_mail = False

        if socket.gethostname() == 'fe-sync.int.kernel.org':
            send_mail = True

        # Load known releases from the release tracker file
        known = []

        if os.path.exists(self.release_tracker):
            try:
                fh = open(self.release_tracker, 'r')
                known = json.load(fh)
                fh.close()
            except:
                # it's better to not announce something than to spam
                # people needlessly.
                send_mail = False

        for chunks in self.current_releases:
            release = chunks[1]
            if release not in known:
                # This appears to be a new release.
                if chunks[5] is None or chunks[6] is None or chunks[7] is None:
                    # Don't announce anything that doesn't have source, patch or sign.
                    continue

                known.append(release)
                if send_mail:
                    self.send_release_email(chunks)

        fh = open(self.release_tracker, 'w')
        json.dump(known, fh, indent=4)
        fh.close()

    def send_release_email(self, chunks):
        (label, release, iseol, timestamp, isodate, source, sign, patch, incr, changelog, gitweb, diffview) = chunks
        if iseol:
            eol = ' (EOL)'
        else:
            eol = ''

        import smtplib
        from email.mime.text import MIMEText
        from email.Utils import COMMASPACE, formatdate, make_msgid

        body = ("Linux kernel version %s%s has been released. It is available from:\r\n" % (release, eol)
                + "\r\n"
                + "Patch:          https://www.kernel.org/%s\r\n" % patch
                + "Full source:    https://www.kernel.org/%s\r\n" % source
                + "PGP Signature:  https://www.kernel.org/%s\r\n" % sign
                + "\r\n"
                + "-----------------------------------------------------------------------------\r\n"
                + "This is an automatically generated message. To unsubscribe from this list,\r\n"
                + "please send a message to majordomo@vger.kernel.org containing the line:\r\n"
                + "\r\n"
                + "\tunsubscribe linux-kernel-announce <your_email_address>\r\n"
                + "\r\n"
                + "... where <your_email_address> is the email address you used to subscribe\r\n"
                + "to this list.\r\n"
                + "-----------------------------------------------------------------------------\r\n")

        if diffview is not None:
            body += ("\r\n"
                + "You can view the summary of the changes at the following URL:\r\n"
                + "%s\r\n" % diffview)

        msg = MIMEText(body)
        msg['Subject'] = "Linux kernel %s released" % release
        msg['From'] = 'Linux Kernel Distribution System <kdist@linux.kernel.org>'
        msg['To'] = 'linux-kernel-announce@vger.kernel.org'
        msg['Bcc'] = 'ftpadmin@kernel.org'
        msg['Date'] = formatdate(localtime=True)
        msg['Message-Id'] = make_msgid('kdist.linux.kernel.org')
        msg['X-Linux-Kernel-Version'] = release
        msg['X-Linux-Kernel-Patch-URL'] = "https://www.kernel.org/%s" % patch
        msg['X-Linux-Kernel-Full-URL'] = "https://www.kernel.org/%s" % source

        s = smtplib.SMTP('mail.kernel.org')
        s.sendmail('kdist@linux.kernel.org', ['linux-kernel-announce@vger.kernel.org', 'ftpadmin@kernel.org'],
                   msg.as_string())
        s.quit()

    def generate_releases_json(self):
        # Put release info into a .json file for easy import and parse
        out = {'releases': []}
        for entry in self.current_releases:
            (label, release, iseol, timestamp, isodate, source, sign, patch, incr, changelog, gitweb, diffview) = entry

            if source:
                source = 'https://www.kernel.org/%s' % source
            if sign:
                sign = 'https://www.kernel.org/%s' % sign
            if patch:
                patch = 'https://www.kernel.org/%s' % patch
            if incr:
                incr = 'https://www.kernel.org/%s' % incr
            if changelog:
                changelog = 'https://www.kernel.org/%s' % changelog

            relhash = {
                'moniker': label,
                'version': release,
                'iseol':   iseol,
                'released': {
                    'timestamp': timestamp,
                    'isodate':   isodate,
                },
                'source': source,
                'pgp': sign,
                'patch': {
                    'full': patch,
                    'incremental': incr,
                },
                'changelog': changelog,
                'gitweb': gitweb,
                'diffview': diffview
            }

            out['releases'].append(relhash)

        out['latest_stable'] = {
            'version': self.latest_release[1],
        }

        fh = open(self.json_path, 'w')
        json.dump(out, fh, indent=4)
        fh.close()

    def generate_finger_banner(self):
        # Just a bit of legacy silliness
        contents = ''
        for chunks in self.current_releases:
            label = chunks[0]
            release = chunks[1]
            iseol = chunks[2]

            if label == 'mainline':
                line = ' 3'
            elif label == 'linux-next':
                line = ''
            else:
                bits = release.split('.')
                bits.pop(-1)
                line = ' ' + '.'.join(bits)

            if iseol:
                eol = ' (EOL)'
            else:
                eol = ''

            leftside = 'The latest %s%s version of the Linux kernel is:' % (label, line)
            contents += '{0:<61} {1}{2}\n'.format(leftside, release, eol)

        fp = open(self.finger_path, 'w')
        fp.write(contents)
        fp.close()

    def generate_rss_feed(self):
        feed = Rss201rev2Feed(
            title='Latest Linux Kernel Versions',
            link='http://www.kernel.org',
            feed_url='http://www.kernel.org/feeds/kdist.xml',
            description='Latest Linux Kernel Versions',
            creator='FTP Admin <ftpadmin@kernel.org>'
        )
        for entry in self.current_releases:
            (label, release, iseol, timestamp, isodate, source, sign, patch, incr, changelog, gitweb, diffview) = entry

            if iseol:
                eol = ' (EOL)'
            else:
                eol = ''

            contents = '''
            <table>
                <tr><th align="right">Version:</th><td><strong>%s%s</strong> (%s)</td></tr>
                <tr><th align="right">Released:</th><td>%s</td></tr>
            ''' % (release, eol, label, isodate)

            if source:
                contents += '''
                <tr><th align="right">Source:</th><td><a href="https://www.kernel.org/%s">linux-%s.tar.xz</a></td></tr>''' % (source, release)

            if sign:
                contents += '''
                <tr><th align="right">PGP Signature:</th><td><a href="https://www.kernel.org/%s">linux-%s.tar.sign</a></td></tr>''' % (sign, release)

            if patch:
                contents += '''
                <tr><th align="right">Patch:</th><td><a href="https://www.kernel.org/%s">patch-%s.xz</a>''' % (patch, release)
                if incr:
                    contents += ''' (<a href="https://www.kernel.org/%s">Incremental</a>)''' % incr
                contents += '''</td></tr>'''

            if changelog:
                contents += '''
                <tr><th align="right">ChangeLog:</th><td><a href="https://www.kernel.org/%s">ChangeLog-%s</a></td></tr>''' % (changelog, release)

            contents += '''
            </table>'''

            feed.add_item(
                title='%s: %s' % (release, label),
                link='http://www.kernel.org/',
                unique_id='kernel.org,%s,%s,%s' % (label, release, isodate),
                description=contents,
                pubdate=datetime.datetime.fromtimestamp(timestamp)
            )

        # We really should be generating after site is done,
        # but I'm too lazy to figure out the plugin hooks for that
        utils.mkdir_p(os.path.dirname(self.rss_path))

        fp = open(self.rss_path, 'w')
        feed.write(fp, 'utf-8')
        fp.close()

    def _get_release_dir_by_version(self, version):
        # some magic here to calculate where the source is
        urlpath = 'pub/linux/kernel'

        if version.find('3.') == 0:
            # This is version 3.x, so will be in /v3.x/
            urlpath += '/v3.x'

        elif version.find('4.') == 0:
            # When Linus feels like releasing a 4.x, it'll be in /v4.x/
            urlpath += '/v4.x'

        elif version.find('2.6') == 0:
            # We're hardcoding ourselves here, but this will rarely change
            urlpath += '/v2.6/longterm'

            if version.find('2.6.32') == 0:
                urlpath += '/v2.6.32'
            else:
                urlpath += '/v2.6.34'

        if version.find('-rc') > 0:
            # This is a testing kernel, so will be in /testing/
            urlpath += '/testing'

        return urlpath

    def _get_source_path_by_version(self, version):
        dirpath = self._get_release_dir_by_version(version)
        path = '%s/linux-%s.tar.xz' % (dirpath, version)

        return path

    def _get_sign_path_by_version(self, version):
        dirpath = self._get_release_dir_by_version(version)
        path = '%s/linux-%s.tar.sign' % (dirpath, version)

        return path

    def _get_patch_path_by_version(self, version):
        dirpath = self._get_release_dir_by_version(version)
        path = '%s/patch-%s.xz' % (dirpath, version)

        return path

    def _get_prev_release(self, release, label):
        # Returns (previous mainline, previous incremental)
        # for 3.17-rc2:  (3.16, 3.17-rc1)
        # for 3.16.2:    (3.16, 3.16.1)
        # for 2.6.32.63: (2.6.32, 2.6.32.62)
        # for 3.17-rc1:  (3.16, None)
        # for 3.17:      (3.16, None)
        # for 3.16.1:    (3.16, None)

        if release.find('next') != -1:
            # Futile for next kernels, as we have to look at actual tags
            return None, None

        bits = release.split('.')

        if len(bits) < 2:
            # What happen? Someone set up us something weird.
            return None, None

        mainline = None
        incremental = None

        if label.find('mainline') == 0:
            # Does the last bit have '-rc' in it?
            if bits[-1].find('-rc') > 0:
                rcbits = bits[-1].split('-rc')
                try:
                    lastbit = int(rcbits.pop(-1))
                    mainlbit = int(rcbits.pop(-1))

                    if lastbit > 1:
                        # We have an incremental
                        prevbit = str(lastbit - 1)
                        prevrc = '%s-rc%s' % (mainlbit, prevbit)
                        newbits = bits[:-1] + [prevrc]
                        incremental = '.'.join(newbits)
                    # Now arrive at mainline
                    if mainlbit == 0:
                        # We're looking at 4.0-rcX, then. Cowardly bail out with only incremental
                        return None, incremental
                    prevbit = str(mainlbit - 1)
                    newbits = bits[:-1] + [prevbit]
                    mainline = '.'.join(newbits)

                except ValueError:
                    pass

                return mainline, incremental

            # First, most unusual case -- a mainline release ending in .0
            try:
                lastbit = int(bits.pop(-1))
                if lastbit == 0:
                    # We can't really figure out what the previous release was based on this info, so
                    # we cowardly pretend it didn't happen
                    return None, None

                prevbit = str(lastbit - 1)
                bits.append(prevbit)
                mainline = '.'.join(bits)
            except ValueError:
                # Not sure what happened, but let's pretend it didn't work
                return None, None
            
            return mainline, incremental

        # Not a mainline kernel, so a simpler logic
        try:
            lastbit = int(bits.pop(-1))
            # Combining the remaining bits gives us mainline
            mainline = '.'.join(bits)

            if lastbit > 1:
                prevbit = str(lastbit - 1)
                bits.append(prevbit)
                incremental = '.'.join(bits)
            else:
                # We don't have a previous incremental in this case
                incremental = None

            return mainline, incremental

        except ValueError:
            # Not sure what happened, but let's pretend it didn't work
            return None, None

        return None, None


    def make_release_line(self, rel, label, iseol=False):
        # drop the leading 'v':
        if rel[0][0] == 'v':
            release = rel[0][1:]
        else:
            release = rel[0]

        timestamp = rel[1]
        isodate = time.strftime('%Y-%m-%d', time.gmtime(rel[1]))

        source = None
        sign = None
        patch = None
        incr = None
        changelog = None
        gitweb = None
        diffview = None

        if release.find('next') != 0:
            # next don't have anything besides a tag

            source = self._get_source_path_by_version(release)
            sign = self._get_sign_path_by_version(release)
            patch = self._get_patch_path_by_version(release)

            prevmainline, previncremental = self._get_prev_release(release, label)

            if label.find('stable') == 0 or label.find('longterm') == 0:
                dirpath = self._get_release_dir_by_version(release)
                changelog = '%s/ChangeLog-%s' % (dirpath, release)
                cgitpath = 'https://git.kernel.org/cgit/linux/kernel/git/stable/linux-stable.git'
                gitweb = ('%s/log/?id=refs/tags/v%s' % (cgitpath, release))

                # incr patches are named incr/3.5.(X-1)-(X).xz
                if previncremental:
                    lastbit = release.split('.')[-1]
                    incr = '%s/incr/patch-%s-%s.xz' % (dirpath, previncremental, lastbit)
                    diffview = '%s/diff/?id=v%s&id2=v%s' % (cgitpath, release, previncremental)
                elif prevmainline:
                    # diffview to previous mainline
                    diffview = ('%s/diff/?id=v%s&id2=v%s' % (cgitpath, release, prevmainline))
                        
            elif label.find('mainline') == 0:
                cgitpath = 'https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git'
                gitweb = '%s/log/?id=refs/tags/v%s' % (cgitpath, release)
                if previncremental:
                    diffview = '%s/diff/?id=v%s&id2=v%s' % (cgitpath, release, previncremental)
                elif prevmainline:
                    diffview = ('%s/diff/?id=v%s&id2=v%s' % (cgitpath, release, prevmainline))

        else:
            gitweb = 'https://git.kernel.org/cgit/linux/kernel/git/next/linux-next.git/log/?id=refs/tags/%s' % release
            # Not offering a diffview, as it's too hard to calculate
            diffview = None

        # Verify that source, patch, changelog and incremental patch exist
        if source and not os.path.exists('%s/%s' % (self.pub_mount, source)):
            source = None
        if sign and not os.path.exists('%s/%s' % (self.pub_mount, sign)):
            sign = None
        if patch and not os.path.exists('%s/%s' % (self.pub_mount, patch)):
            patch = None
        if changelog and not os.path.exists('%s/%s' % (self.pub_mount, changelog)):
            changelog = None
        if incr and not os.path.exists('%s/%s' % (self.pub_mount, incr)):
            incr = None

        # This needs to be refactored into a hash. In my defense,
        # it started with 3 entries.
        return label, release, iseol, timestamp, isodate, source, sign, patch, incr, changelog, gitweb, diffview

    def get_tagref_list(self, repo, cutoff=None):
        tagrefs = []
        for tagref in repo.tags:
            try:
                tdate = tagref.tag.tagged_date
            except:
                # Some of the tags break git-python due to not having an associated
                # commit. Work around this limitation by ignoring those tags.
                continue

            # Is it too old?
            if cutoff is not None and tdate < cutoff:
                continue

            tagrefs.append(tagref)

        return tagrefs

    def _check_tarball_by_tagname(self, tagname):
        # Only check those starting with "v"
        if tagname[0] == 'v':
            # Ignore this check for next-YYYYMMDD kernels
            source = self._get_source_path_by_version(tagname[1:])

            if not os.path.exists('%s/%s' % (self.pub_mount, source)):
                return False

        return True

    def find_latest_matching(self, tagrefs, regex, check_tarball=True):
        current = None

        for tagref in tagrefs:
            tdate = tagref.tag.tagged_date

            # Does it match the regex?
            if not regex.match(tagref.name):
                continue

            # is it older than current?
            if current is None or current.tag.tagged_date < tdate:
                if not self._check_tarball_by_tagname(tagref.name):
                    continue

                current = tagref

        if current is None:
            return None

        return current.name, current.tag.tagged_date

