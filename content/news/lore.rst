List archives on lore.kernel.org
================================

:category: Site news
:slug: lore

You may access the archives of many Linux development mailing lists on
lore.kernel.org_. Most of them include a full archive of messages going
back several decades.

.. table:: Currently hosted lists

    ===================== ==============================================
    LKML                  https://lore.kernel.org/lkml/
    backports             https://lore.kernel.org/backports/
    cocci                 https://lore.kernel.org/cocci/
    kernelnewbies         https://lore.kernel.org/kernelnewbies/
    linux-amlogic         https://lore.kernel.org/linux-amlogic/
    linux-arm-kernel      https://lore.kernel.org/linux-arm-kernel/
    linux-block           https://lore.kernel.org/linux-block/
    linux-bluetooth       https://lore.kernel.org/linux-bluetooth/
    linux-btrfs           https://lore.kernel.org/linux-btrfs/
    linux-clk             https://lore.kernel.org/linux-clk/
    linux-i3c             https://lore.kernel.org/linux-i3c/
    linux-iio             https://lore.kernel.org/linux-iio/
    linux-integrity       https://lore.kernel.org/linux-integrity/
    linux-media           https://lore.kernel.org/linux-media/
    linux-mips            https://lore.kernel.org/linux-mips/
    linux-modules         https://lore.kernel.org/linux-modules/
    linux-nfs             https://lore.kernel.org/linux-nfs/
    linux-parisc          https://lore.kernel.org/linux-parisc/
    linux-pci             https://lore.kernel.org/linux-pci/
    linux-riscv           https://lore.kernel.org/linux-riscv/
    linux-renesas-soc     https://lore.kernel.org/linux-renesas-soc/
    linux-rtc             https://lore.kernel.org/linux-rtc/
    linux-security-module https://lore.kernel.org/linux-security-module/
    linux-sgx             https://lore.kernel.org/linux-sgx/
    linux-wireless        https://lore.kernel.org/linux-wireless/
    linuxppc-dev          https://lore.kernel.org/linuxppc-dev/
    selinux               https://lore.kernel.org/selinux/
    selinux-refpolicy     https://lore.kernel.org/selinux-refpolicy/
    util-linux            https://lore.kernel.org/util-linux/
    wireguard             https://lore.kernel.org/wireguard/
    ===================== ==============================================

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
