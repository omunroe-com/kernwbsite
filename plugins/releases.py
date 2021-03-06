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

import requests

from distutils.version import StrictVersion

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

        self.rss_path = os.path.join(generator.output_path, 'feeds', 'kdist.xml')
        self.finger_path = os.path.join(generator.output_path, 'finger_banner')
        self.json_path = os.path.join(generator.output_path, 'releases.json')

        self.gitsite = 'https://git.kernel.org'
        self.wwwsite = 'https://cdn.kernel.org'
        self.checksite = 'https://mirrors.edge.kernel.org'

        self.reqs = requests.Session()

        settings = generator.settings

        GIT_MAINLINE = settings.get('GIT_MAINLINE')
        GIT_STABLE = settings.get('GIT_STABLE')
        GIT_NEXT = settings.get('GIT_NEXT')

        LONGTERM_KERNELS = settings.get('LONGTERM_KERNELS')
        EOL_KERNELS = settings.get('EOL_KERNELS')

        self.MAJOR_JUMPS = settings.get('MAJOR_JUMPS')

        self.release_tracker = settings.get('RELEASE_TRACKER')

        repo = Repo(GIT_MAINLINE)
        tagrefs = self.get_tagref_list(repo)

        rc_reg = re.compile('v.*-rc\d+$')
        mainline_rc = self.find_latest_matching(tagrefs, rc_reg)
        rel_reg = re.compile('v[^-]*\d+$')
        mainline_rel = self.find_latest_matching(tagrefs, rel_reg)

        # if mainline_rel is newer than mainline_rc, ignore mainline_rc
        if mainline_rc[1] < mainline_rel[1]:
            mainline_rc = None

        # Move on to the stable repo
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
                if tagref.name.find(ver+'.') == 1:
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

        stable = sorted(stable, key=lambda x: StrictVersion(x[0][1:]), reverse=True)

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
                if rel[0].find(eolrel + '.') == 1:
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
                    if found[0].find(eolrel + '.') == 1:
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

    def check_url_exists(self, url):
        checkurl = url.replace(self.wwwsite, self.checksite)
        r = self.reqs.head(checkurl)
        return r.status_code == 200

    def check_release_tracker(self):
        if 'PELICAN_DRYRUN' in os.environ.keys():
            print 'PELICAN_DRYRUN found, not doing release tracking'
            return

        import socket
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
                if chunks[5] is None:
                    # Don't announce anything that doesn't have source.
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
        from email.Utils import COMMASPACE, formatdate

        announce_list = 'linux-kernel-announce@vger.kernel.org'
        smtp_server = 'mail.kernel.org'

        # This allows us to run tests in pre-prod
        if 'ANNOUNCE_LIST' in os.environ.keys():
            announce_list = os.environ['ANNOUNCE_LIST']
        if 'SMTP_SERVER' in os.environ.keys():
            smtp_server = os.environ['SMTP_SERVER']

        body = ( "Linux kernel version %s%s is now available:\r\n" % (release, eol)
               + "\r\n"
               + "Full source:    %s" % source)

        if patch is not None:
            body += ( "\r\n"
                    + "Patch:          %s" % patch)

        if sign is not None:
            body += ( "\r\n"
                    + "PGP Signature:  %s" % sign)

        if diffview is not None:
            body += ( "\r\n\r\n"
                    + "You can view the summary of the changes at the following URL:\r\n"
                    + "%s\r\n\r\n" % diffview)

        msg = MIMEText(body)
        msg['Subject'] = "Linux kernel %s released" % release
        msg['From'] = 'Linux Kernel Distribution System <kdist@linux.kernel.org>'
        msg['To'] = announce_list
        msg['Date'] = formatdate(localtime=True)
        msg['Message-Id'] = '<%s.release-%s@kdist.linux.kernel.org>' % (
            datetime.date.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S'), release)
        msg['X-Linux-Kernel-Version'] = release
        msg['X-Linux-Kernel-Full-URL'] = source

        if patch is not None:
            msg['X-Linux-Kernel-Patch-URL'] = patch

        s = smtplib.SMTP(smtp_server)
        s.sendmail('kdist@linux.kernel.org', [announce_list,], msg.as_string())
        s.quit()

    def generate_releases_json(self):
        # Put release info into a .json file for easy import and parse
        out = {'releases': []}
        for entry in self.current_releases:
            (label, release, iseol, timestamp, isodate, source, sign, patch, incr, changelog, gitweb, diffview) = entry

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
            line = ''

            if label not in ('mainline', 'linux-next'):
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
                <tr><th align="right">Source:</th><td><a href="%s">%s</a></td></tr>''' % (source, os.path.basename(source))

            if sign:
                contents += '''
                <tr><th align="right">PGP Signature:</th><td><a href="%s">%s</a></td></tr>''' % (sign, os.path.basename(sign))

            if patch:
                contents += '''
                <tr><th align="right">Patch:</th><td><a href="%s">full</a>''' % patch
                if incr:
                    contents += ''' (<a href="%s">incremental</a>)''' % incr
                contents += '''</td></tr>'''

            if changelog:
                contents += '''
                <tr><th align="right">ChangeLog:</th><td><a href="%s">%s</a></td></tr>''' % (changelog, os.path.basename(changelog))

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
        urlpath = 'pub/linux/kernel/v%s.x' % version[0]

        return urlpath

    def _get_source_path_by_version(self, version):
        dirpath = self._get_release_dir_by_version(version)
        path = '%s/%s/linux-%s.tar.xz' % (self.wwwsite, dirpath, version)

        return path

    def _get_sign_path_by_version(self, version):
        dirpath = self._get_release_dir_by_version(version)
        path = '%s/%s/linux-%s.tar.sign' % (self.wwwsite, dirpath, version)

        return path

    def _get_patch_path_by_version(self, version):
        dirpath = self._get_release_dir_by_version(version)
        path = '%s/%s/patch-%s.xz' % (self.wwwsite, dirpath, version)

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
                        # We're looking at X.0-rcX. Use the MAJOR_JUMPS mapping
                        if bits[0] in self.MAJOR_JUMPS:
                            return self.MAJOR_JUMPS[bits[0]], incremental
                        # Linus doesn't pre-announce major jumps...
                        # so just return None until we add it to the mapping.
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
                    # Use MAJOR_JUMPS mapping again
                    if bits[0] in self.MAJOR_JUMPS:
                        return self.MAJOR_JUMPS[bits[0]], None
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
                changelog = '%s/%s/ChangeLog-%s' % (self.wwwsite, dirpath, release)
                cgitpath = 'stable'
                gitweb = '%s/%s/h/v%s' % (self.gitsite, cgitpath, release)

                # incr patches are named incr/3.5.(X-1)-(X).xz
                if previncremental:
                    lastbit = release.split('.')[-1]
                    incr = '%s/%s/incr/patch-%s-%s.xz' % (self.wwwsite, dirpath, previncremental, lastbit)
                    diffview = '%s/%s/ds/v%s/v%s' % (self.gitsite, cgitpath, release, previncremental)
                elif prevmainline:
                    # diffview to previous mainline
                    diffview = '%s/%s/ds/v%s/v%s' % (self.gitsite, cgitpath, release, prevmainline)

            elif label.find('mainline') == 0:
                cgitpath = 'torvalds'
                gitweb = '%s/%s/h/v%s' % (self.gitsite, cgitpath, release)
                # if it's an -rc kernel, link to tarball and patch generated by cgit
                if release.find('-rc') > 0:
                    # -rc kernel tarball/patches are cgit-generated and have no signatures
                    sign = None
                    source = '%s/%s/t/linux-%s.tar.gz' % (self.gitsite, cgitpath, release)
                    patch = '%s/%s/p/v%s/v%s' % (self.gitsite, cgitpath, release, prevmainline)
                    if previncremental:
                        incr = '%s/%s/p/v%s/v%s' % (self.gitsite, cgitpath, release, previncremental)

                if previncremental:
                    diffview = '%s/%s/ds/v%s/v%s' % (self.gitsite, cgitpath, release, previncremental)
                elif prevmainline:
                    diffview = '%s/%s/ds/v%s/v%s' % (self.gitsite, cgitpath, release, prevmainline)

        else:
            gitweb = '%s/next/linux-next/h/%s' % (self.gitsite, release)
            # Not offering a diffview, as it's too hard to calculate
            diffview = None

        # if not -rc kernels, verify that patch, changelog and incremental patch exist
        if release.find('-rc') < 0:
            if patch and not self.check_url_exists(patch):
                patch = None
            if changelog and not self.check_url_exists(changelog):
                changelog = None
            if incr and not self.check_url_exists(incr):
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
        if tagname[0] == 'v' and tagname.find('-rc') < 0:
            # Ignore this check for -rc and next-YYYYMMDD kernels
            source = self._get_source_path_by_version(tagname[1:])

            if not self.check_url_exists(source):
                return False

        return True

    def find_latest_matching(self, tagrefs, regex, blacklist=[]):
        current = None

        for tagref in tagrefs:
            # Does it match the regex?
            if not regex.match(tagref.name):
                continue

            if tagref.name in blacklist:
                continue

            tdate = tagref.tag.tagged_date

            # is it older than current?
            if current is None or current.tag.tagged_date < tdate:
                current = tagref

        if current is None:
            return None

        if not self._check_tarball_by_tagname(current.name):
            # Tarball for the latest tag does not exist.
            # Add it to blacklist and try again.
            blacklist.append(current.name)
            return self.find_latest_matching(tagrefs, regex, blacklist)

        return current.name, current.tag.tagged_date

