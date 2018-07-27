Minor changes to kernel tarball releases
========================================

:category: Site news
:slug: minor-changes-to-tarball-release-format

We'd like to announce several small changes to the way Linux tarballs
are produced.

Mainline release tarball signatures
-----------------------------------
Starting with the 4.18 final release, all mainline tarball PGP
signatures will be made by Greg Kroah-Hartman instead of Linus Torvalds.
The main goal behind this change is to simplify the `verification
process`_ and make all kernel tarball releases available for download on
kernel.org be signed by the same developer.

Linus Torvalds will continue to PGP-sign all tags in the mainline
git repository. They can be verified using the ``git verify-tag``
command.

.. _`verification process`: https://www.kernel.org/signature.html

Sunsetting .gz tarball generation
---------------------------------
We stopped creating .bz2 copies of tarball releases 5 years ago, and the
time has come to stop producing .gz duplicate copies of all our content
as well, as XZ tools and libraries are now available on all major
platforms. Starting September 1st, 2018, all tarball releases available
via ``/pub`` download locations will only be available in XZ-compressed
format.

If you absolutely must have .gz compressed tarballs, you may obtain them
from git.kernel.org by following snapshot download links in the
appropriate repository view.

No future PGP signatures on patches and changelogs
--------------------------------------------------
For legacy purposes, we will continue to provide pre-generated
changelogs and patches (both to the previous mainline and incremental
patches to previous stable). However, from now on they will be generated
by automated processes and will no longer carry detached PGP signatures.
If you require cryptographically verified patches, please generate them
directly from the `stable git repository`_ after verifying the PGP
signatures on the tags using ``git verify-tag``.

.. _`stable git repository`: https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
