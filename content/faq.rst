Frequently asked questions
==========================

:slug: faq
:category: FAQ

If you have questions, comments or concerns about the F.A.Q. please
contact us at webmaster@kernel.org.

Is Linux Kernel Free Software?
------------------------------
Linux kernel is released under GNU GPL version 2 and is therefore Free
Software as defined by the `Free Software Foundation`_. You may read the
entire copy of the license in the COPYING_ file distributed with each
release of the Linux kernel.

.. _`Free Software Foundation`: https://www.fsf.org/
.. _COPYING: /pub/linux/kernel/COPYING

What does "stable/EOL" and "longterm" mean?
-------------------------------------------
As kernels move from the "mainline" into the "stable" category, two
things can happen:

1. They can reach "End of Life" after a few bugfix revisions, which
   means that kernel maintainers will release no more bugfixes for this
   kernel version, or
2. They can be put into "longterm" maintenance, which means that
   maintainers will provide bugfixes for this kernel revision for a
   much longer period of time.

If the kernel version you are using is marked "EOL," you should consider
upgrading to the next major version as there will be no more bugfixes
provided for the kernel version you are using.

Please check the Releases_ page for more info.

.. _Releases: |filename|releases.rst

Why is an LTS kernel marked as "stable" on the front page?
----------------------------------------------------------
Long-term support ("LTS") kernels announced on the Releases_ page will
be marked as "stable" on the front page if there are no other current
stable kernel releases. This is done to avoid breaking automated parsers
monitoring kernel.org with an expectation that there will always be a
kernel release marked as "stable."

Is there an RSS feed for the latest kernel version?
---------------------------------------------------
Yes, and you can find it at https://www.kernel.org/feeds/kdist.xml.

We also publish a .json file with the latest release information, which
you can pull from here: https://www.kernel.org/releases.json.

Why are there files that are dated tomorrow?
--------------------------------------------
All timestamps on kernel.org are in UTC (Coordinated Universal Time). If
you live in the western hemisphere your local time lags behind UTC.
Under Linux/Unix, type ``date -u`` to get the current time in UTC.

Can I get an account on kernel.org?
-----------------------------------
Kernel.org accounts are usually reserved for subsystem maintainers or
high-profile developers. It is absolutely not necessary to have an
account on kernel.org to contribute to the development of the Linux
kernel, unless you submit pull requests directly to Linus.

If you are listed in the MAINTAINERS file or have reasons to believe you
should have an account on kernel.org because of the amount of your
contributions, please refer to the `accounts wiki page`_ for the
procedure to follow.

.. _`accounts wiki page`: https://korg.wiki.kernel.org/userdoc/accounts

I have cool project X, can you guys mirror it for me?
-----------------------------------------------------
Probably not. Kernel.org deals with the Linux kernel, various
distributions of the kernel and larger repositories of packages. We do
not mirror individual projects, software, etc as we feel there are
better places providing mirrors for those kinds of repositories. If you
feel that kernel.org should mirror your project, please contact
ftpadmin@kernel.org with the following information:

- name
- project name
- project website
- detailed project description
- reason for wanting us to mirror

The Kernel.org admin team will then review your request and talk to you
about it. As with any kind of account on kernel.org it's up to the
discretion of the admin team.

How does kernel.org provide its users access to the git trees?
--------------------------------------------------------------
We are using an access control system called gitolite_, originally
written and maintained by Sitaram Chamarty. We chose gitolite for a
number of reasons:

- Limiting of ssh access to the system
- Fine grained control over repository access
- Well maintained and supported code base
- Responsive development
- Broad and diverse install base

As well at the time of deployment the code had undergone an external
code review.

.. _gitolite: https://github.com/sitaramc/gitolite/wiki

How do I create an -rc kernel? I get "Reversed patch detected!"
---------------------------------------------------------------
-rc kernel patches are generated from the base stable release.

For example: to create the 2.6.14-rc5 kernel, you must:

- download 2.6.13 (not 2.6.13.4)
- and then apply the 2.6.14-rc5 patch.

Yes, you want 2.6.13, not 2.6.14. Remember, that's an -rc kernel, as in, 2.6.14 doesn't exist yet. :)

Where can I find kernel 2.4.20-3.16?
------------------------------------
Kernel version numbers of this form are distribution kernels, meaning
they are modified kernels produced by distributions. Please contact the
relevant distributor; or check out https://mirrors.kernel.org/.

See the Releases_ page for more info on distribution kernels.

.. _Releases: |filename|releases.rst

I need help building/patching/fixing Linux kernel/modules/drivers!
------------------------------------------------------------------
Please see the `Kernel Newbies`_ website.

There is also a wealth of knowledge on many topics involving Linux at
The Linux Documentation Project (http://www.tldp.org)

For finding or reporting bugs, look through the archives for the various
Linux mailing lists, and if no specific list seems appropriate, try the
browsing the Linux Kernel Mailing List.

.. _`Kernel Newbies`: http://kernelnewbies.org/

What happened to ftp.kernel.org?
--------------------------------
FTP service was terminated on March 1, 2017. All content that used to be
available via ftp.kernel.org can be accessed by browsing
https://www.kernel.org/pub/. If you would like to use a command-line
tool for accessing these files, you can do so with lftp:

    lftp https://www.kernel.org/pub

When will the next kernel be released?
--------------------------------------
The next kernel will be released when it is ready. There is no strict
timeline for making releases, but if you really need an educated guess,
visit the Linux kernel `PHB Crystal Ball`_ -- it tries to provide a
ballpark guess based on previous kernel release schedule.

.. _`PHB Crystal Ball`: http://phb-crystal-ball.org/

What will go into the next release?
-----------------------------------
It is hard to predict with certainty, but you can either take a peek at
`linux-next`_ or read the `Linux Weather Forecast`_, where Jonathan
Corbet provides a broad forecast of what will likely be included into
the next mainline release.

.. _`linux-next`: https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/
.. _`Linux Weather Forecast`: https://www.linux.com/news/2017/7/linux-weather-forecast
