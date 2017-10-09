#!/usr/bin/env python
# -*- coding: utf-8 -*- #
SITENAME = u'The Linux Kernel Archives'
SITEURL  = u'https://www.kernel.org'

TIMEZONE = 'UTC'

DEFAULT_LANG = u'en'

DATE_FORMATS = {
        u'en': u'%Y-%m-%d',
    }

DEFAULT_DATE = ('fs')
FILENAME_METADATA = u'.*(?P<date>\d{4}-\d{2}-\d{2}).*'

#ARTICLE_URL = u'posts/{date:%Y}-{date:%m}-{date:%d}/{slug}.html'
#ARTICLE_SAVE_AS = u'posts/{date:%Y}-{date:%m}-{date:%d}/{slug}.html'

# Dirs to always push to site
STATIC_PATHS = (['corporate', 'images', 'news/images'])

import os
import sys
sys.path.append('./')
from plugins import releases

LONGTERM_KERNELS = ('4.9', '4.4', '4.1', '3.18', '3.16', '3.14', '3.12', '3.10', '3.2')
EOL_KERNELS = ('3.4', '3.12', '3.14', '3.18', '3.19', '4.0', '4.2', '4.3', '4.5', '4.6', '4.7', '4.8', '4.10', '4.11', '4.12')

if 'GIT_REPOS' in os.environ.keys():
    GIT_REPOS = os.environ['GIT_REPOS']
else:
    GIT_REPOS = '/mnt/git-repos/repos'

if 'PELICAN_STATEDIR' in os.environ.keys():
    PELICAN_STATEDIR = os.environ['PELICAN_STATEDIR']
else:
    PELICAN_STATEDIR = '/var/lib/mirror'

GIT_MAINLINE = os.path.join(GIT_REPOS, 'pub/scm/linux/kernel/git/torvalds/linux.git')
GIT_STABLE   = os.path.join(GIT_REPOS, 'pub/scm/linux/kernel/git/stable/linux-stable.git')
GIT_NEXT     = os.path.join(GIT_REPOS, 'pub/scm/linux/kernel/git/next/linux-next.git')

RELEASE_TRACKER = os.path.join(PELICAN_STATEDIR, 'release-tracker.json')

PLUGINS = [releases]

# Blogroll
LINKS =  (
    ('Cgit', 'https://git.kernel.org/'),
    ('Wikis', 'https://www.wiki.kernel.org/'),
    ('Bugzilla', 'https://bugzilla.kernel.org/'),
    ('Patchwork', 'https://patchwork.kernel.org/'),
    ('Kernel Mailing Lists', 'http://vger.kernel.org/'),
    ('Mirrors', 'https://mirrors.kernel.org/'),
    ('Linux.com', 'https://www.linux.com/'),
    ('Linux Foundation', 'http://www.linuxfoundation.org/'),
    ('Kernel Planet', 'http://planet.kernel.org/'),
)

# Social widget
SOCIAL = (
    ('Linux on Google+', 'https://plus.google.com/+Linux/posts'),
)

THEME = './korgi'
DEFAULT_PAGINATION = 10
