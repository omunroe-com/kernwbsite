List archives on lore.kernel.org
================================

:category: About
:slug: lore

You may access the archives of many Linux development mailing lists on
lore.kernel.org_. Most of them include a full archive of messages going
back several decades.

.. table:: Currently hosted lists

    ============== =======================================
    LKML           https://lore.kernel.org/lkml/
    linux-pci      https://lore.kernel.org/linux-pci/
    linux-wireless https://lore.kernel.org/linux-wireless/
    wireguard      https://lore.kernel.org/wireguard/
    ============== =======================================

If you would like to suggest another kernel development mailing list to
be included in this list, please follow the instructions on the
following wiki page:

- `Adding list archives to lore.kernel.org`_

Archiving software
------------------
The software managing the archive is called `Public Inbox`_ and offers
the following features:

- Fast, searchable web archives
- Atom feeds per list or per individual thread
- Downloadable mbox archives to make replying easy
- Git-backed archival mechanism you can clone and pull
- Read-only nntp gateway

We collected many list archives going as far back as 1998, and they are
now all available to anyone via a simple git clone. We would like to
extend our thanks to everyone who helped in this effort by donating
their personal archives.

Obtaining full list archives
----------------------------
Git clone URLs are provided at the bottom of each page. Note, that due
mailing list volume, list archives are sharded into multiple
repositories, each roughly 1GB in size. In addition to cloning from
lore.kernel.org, you may also access these repositories on
git.kernel.org_.

Linking to list discussions from commits
----------------------------------------
If you need to reference a mailing list discussion inside code comments
or in a git commit message, please use the "permalink" URL provided by
public-inbox. It is available in the headers of each displayed message
or thread discussion.

.. _lore.kernel.org: https://lore.kernel.org/lkml/
.. _`Adding list archives to lore.kernel.org`: https://korg.wiki.kernel.org/userdoc/lore
.. _`Public Inbox`: https://public-inbox.org/design_notes.html
.. _git.kernel.org: https://git.kernel.org/pub/scm/public-inbox/
