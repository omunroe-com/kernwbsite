Nitrokey digital tokens for kernel developers
=============================================

:category: Site news
:author: Konstantin Ryabitsev

The Linux Foundation IT team has been working to improve the code
integrity of git repositories hosted at kernel.org by promoting the use
of PGP-signed git tags and commits. Doing so allows anyone to easily
verify that git repositories have not been altered or tampered with no
matter from which worldwide mirror they may have been cloned. If the
digital signature on your cloned repository matches the PGP key
belonging to Linus Torvalds or any other maintainer, then you can be
assured that what you have on your computer is the exact replica of the
kernel code without any omissions or additions.

To help promote the use of PGP signatures in Linux kernel development,
we now offer a detailed guide within the kernel documentation tree:

- `Kernel Maintainer PGP Guide`_

.. image:: |filename|images/nitrokey-logo.png
  :height: 70px
  :width: 207px
  :alt: Nitrokey logo
  :align: left

Further, we are happy to announce a new special program sponsored by
`The Linux Foundation`_ in partnership with Nitrokey_ -- the developer
and manufacturer of smartcard-compatible digital tokens capable of
storing private keys and performing PGP operations on-chip. Under this
program, any developer who is listed as a maintainer in the MAINTAINERS_
file, or who has a kernel.org account can qualify for a free digital
token to help improve the security of their PGP keys. The cost of the
device, including any taxes, shipping and handling will be covered by
The Linux Foundation.

To participate in this program, please access the special store front
on the Nitrokey website:

- `Nitrokey Start for Kernel Developers`_

Who qualifies for this program?
-------------------------------
To qualify for the program, you need to have an account at kernel.org or
have your email address listed in the MAINTAINERS_ file (following the
"``M:``" heading). If you do not currently qualify but think you should,
the easiest course of action is to get yourself added to the MAINTAINERS
file or to `apply for an account at kernel.org`_.

Which devices are available under this program?
-----------------------------------------------
The program is limited to `Nitrokey Start`_ devices. There are several
reasons why we picked this particular device among several available
options.

First of all, many Linux kernel developers have a strong preference not
just for open-source software, but for open hardware as well. Nitrokey
is one of the few companies selling GnuPG-compatible smartcard devices
that provide both, since Nitrokey Start is based on Gnuk cryptographic
token firmware developed by `Free Software Initiative of Japan`_. It is
also one of the few commercially available devices that offer native
support for ECC keys, which are both faster computationally than large
RSA keys and generate smaller digital signatures. With our push to use
more code signing of git objects themselves, both the open nature of the
device and its support for fast modern cryptography were key points in
our evaluation.

Additionally, Nitrokey devices (both Start and Pro models) are already
`used by open-source developers`_ for cryptographic purposes and they
are known to work well with Linux workstations.

What is the benefit of digital smartcard tokens?
------------------------------------------------
With usual GnuPG operations, the private keys are stored in the home
directory where they can be stolen by malware or exposed via other
means, such as poorly secured backups. Furthermore, each time a GnuPG
operation is performed, the keys are loaded into system memory and can
be stolen from there using sufficiently advanced techniques (the likes
of Meltdown and Spectre).

A digital smartcard token like Nitrokey Start contains a cryptographic
chip that is capable of storing private keys and performing crypto
operations directly on the token itself. Because the key contents never
leave the device, the operating system of the computer into which the
token is plugged in is not able to retrieve the private keys themselves,
therefore significantly limiting the ways in which the keys can be
leaked or stolen.

Questions or problems?
----------------------
If you qualify for the program, but encounter any difficulties
purchasing the device, please contact Nitrokey at shop@nitrokey.com.

For any questions about the program itself or with any other comments,
please reach out to info@linuxfoundation.org.

.. _`Kernel Maintainer PGP Guide`: https://www.kernel.org/doc/html/latest/process/maintainer-pgp-guide.html
.. _`The Linux Foundation`: https://linuxfoundation.org/
.. _Nitrokey: https://www.nitrokey.com/
.. _MAINTAINERS: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/MAINTAINERS
.. _`Nitrokey Start for Kernel Developers`: https://kernel.nitrokey.com/
.. _`apply for an account at kernel.org`: https://korg.wiki.kernel.org/userdoc/accounts
.. _`Nitrokey Start`: https://shop.nitrokey.com/shop/product/nitrokey-start-6
.. _`Free Software Initiative of Japan`: https://www.fsij.org/category/gnuk.html
.. _`used by open-source developers`: https://lwn.net/Articles/736231/
