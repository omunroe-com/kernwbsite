Linux kernel releases PGP signatures
====================================

:date: 2018-02-15
:slug: signature
:category: Signatures

All kernel releases are cryptographically signed using OpenPGP-compliant
signatures. Everyone is strongly encouraged to verify the integrity of
downloaded kernel releases by verifying the corresponding signatures.

Basic concepts
--------------
Every kernel release comes with a cryptographic signature from the
person making the release. This cryptographic signature allows anyone to
verify whether the files have been modified or otherwise tampered with
after the developer created and signed them. The signing and
verification process uses public-key cryptography and it is next to
impossible to forge a PGP signature without first gaining access to the
developer's private key. If this does happen, the developers will revoke
the compromised key and will re-sign all their previously signed
releases with the new key.

To learn more about the way PGP works, please consult Wikipedia_.

.. _Wikipedia: https://en.wikipedia.org/wiki/Pretty_Good_Privacy#How_PGP_encryption_works

Kernel.org web of trust
-----------------------
PGP keys used by members of kernel.org are cross-signed by other members
of the Linux kernel development community (and, frequently, by many
other people). If you wanted to verify the validity of any key belonging
to a member of kernel.org, you could review the list of signatures on
their public key and then make a decision whether you trust that key or
not. See the `Wikipedia article`_ on the subject of the Web of Trust.

.. _`Wikipedia article`: https://en.wikipedia.org/wiki/Web_of_trust

Using the Web Key Directory
---------------------------
If the task of maintaining your own web of trust is too daunting to you,
you can opt to shortcut this process by using the "Trust on First Use"
(TOFU) approach and rely on the kernel.org Web Key Directory (WKD).

To import keys belonging to many kernel developers, you can use the
following command::

    $ gpg2 --locate-keys [username]@kernel.org

For example, to import keys belonging to Linus Torvalds and Greg
Kroah-Hartman, you would use::

    $ gpg2 --locate-keys torvalds@kernel.org gregkh@kernel.org

This command will verify the TLS certificate presented by kernel.org
before importing these keys into your keyring.

Using GnuPG to verify kernel signatures
---------------------------------------
All software released via kernel.org has detached PGP signatures you can
use to verify the integrity of your downloads.

To illustrate the verification process, let's use Linux 4.6.6 release as
a walk-through example. First, use "``curl``" to download the release
and the corresponding signature::

    $ curl -OL https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.6.6.tar.xz
    $ curl -OL https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.6.6.tar.sign

You will notice that the signature is made against the uncompressed
version of the archive. This is done so there is only one signature
required for .gz and .xz compressed versions of the release. Start
by uncompressing the archive, using ``unxz`` in our case::

    $ unxz linux-4.6.6.tar.xz

Now verify the .tar archive against the signature::

    $ gpg2 --verify linux-4.6.6.tar.sign

You can combine these steps into a one-liner::

    $ xz -cd linux-4.6.6.tar.xz | gpg2 --verify linux-4.6.6.tar.sign -

It's possible that you get a "No public key error"::

    gpg: Signature made Wed 10 Aug 2016 06:55:15 AM EDT using RSA key ID 38DBBDC86092693E
    gpg: Can't check signature: No public key

Please use the "``gpg2 --locate-keys``" command listed above to download
the key for Greg Kroah-Hartman and Linus Torvalds and then try again::

    $ gpg2 --locate-keys torvalds@kernel.org gregkh@kernel.org
    $ gpg2 --verify linux-4.6.6.tar.sign
    gpg: Signature made Wed 10 Aug 2016 06:55:15 AM EDT
    gpg:                using RSA key 38DBBDC86092693E
    gpg: Good signature from "Greg Kroah-Hartman <gregkh@kernel.org>" [unknown]
    gpg: WARNING: This key is not certified with a trusted signature!
    gpg:          There is no indication that the signature belongs to the owner.
    Primary key fingerprint: 647F 2865 4894 E3BD 4571  99BE 38DB BDC8 6092 693E

To make the "``WARNING``" message go away you can indicate that you
choose to trust that key using TOFU::

    $ gpg2 --tofu-policy good 38DBBDC86092693E
    $ gpg2 --trust-model tofu --verify linux-4.6.6.tar.sign
    gpg: Signature made Wed 10 Aug 2016 06:55:15 AM EDT
    gpg:                using RSA key 38DBBDC86092693E
    gpg: Good signature from "Greg Kroah-Hartman <gregkh@kernel.org>" [full]
    gpg: gregkh@kernel.org: Verified 1 signature in the past 53 seconds.  Encrypted
         0 messages.

Note that you may have to pass "``--trust-model tofu``" the first time
you run the verify command, but it should not be necessary after that.

The scripted version
~~~~~~~~~~~~~~~~~~~~
If you need to perform this task in an automated environment or simply
prefer a more convenient tool, you can use the following helper script
to properly download and verify Linux kernel tarballs:

 - get-verified-tarball_

Please review the script before adopting it for your needs.

.. _get-verified-tarball: https://git.kernel.org/pub/scm/linux/kernel/git/mricon/korg-helpers.git/tree/get-verified-tarball

Important fingerprints
----------------------
Here are key fingerprints for Linus Torvalds and Greg Kroah-Hartman, who
are most likely to be releasing kernels:

.. table::

    ================== ======================================================
    Developer          Fingerprint
    ================== ======================================================
    Linus Torvalds     ``ABAF 11C6 5A29 70B1 30AB  E3C4 79BE 3E43 0041 1886``
    Greg Kroah-Hartman ``647F 2865 4894 E3BD 4571  99BE 38DB BDC8 6092 693E``
    ================== ======================================================

Please verify the TLS certificate for this site in your browser before
trusting the above information.

If you get "BAD signature"
--------------------------
If at any time you see "BAD signature" output from "``gpg2 --verify``",
please first check the following first:

1. **Make sure that you are verifying the signature against the .tar
   version of the archive, not the compressed (.tar.xz) version.**
2. Make sure the the downloaded file is correct and not truncated or
   otherwise corrupted.

If you repeatedly get the same "BAD signature" output, please email
helpdesk@kernel.org, so we can investigate the problem.

Kernel.org checksum autosigner and sha256sums.asc
-------------------------------------------------
We have a dedicated off-the-network system that connects directly to our
central attached storage and calculates checksums for all uploaded
software releases. The generated ``sha256sums.asc`` file is then signed
with a PGP key generated for this purpose and that doesn't exist outside
of that system.

These checksums are **NOT** intended to replace developer signatures. It
is merely a way for someone to quickly verify whether contents on one of
the many kernel.org mirrors match the contents on the master mirror.
While you may use them to quickly verify whether what you have
downloaded matches what we have on our central storage system, you
should continue to use developer signatures for best assurance.

Kernel releases prior to September, 2011
----------------------------------------
Prior to September, 2011 all kernel releases were signed automatically by
the same PGP key::

    pub   1024D/517D0F0E 2000-10-10 [revoked: 2011-12-11]
          Key fingerprint = C75D C40A 11D7 AF88 9981  ED5B C86B A06A 517D 0F0E
    uid                  Linux Kernel Archives Verification Key <ftpadmin@kernel.org>

Due to the kernel.org systems compromise, this key has been retired and
revoked. **It will no longer be used to sign future releases and you
should NOT use this key to verify the integrity of any archives. It is
almost certain that this key has fallen into malicious hands.**

All kernel releases that were previously signed with this key were
cross-checked and signed with another key, created specifically
for this purpose::

    pub   3072R/C4790F9D 2013-08-08
          Key fingerprint = BFA7 DD3E 0D42 1C9D B6AB  6527 0D3B 3537 C479 0F9D
    uid   Linux Kernel Archives Verification Key
          (One-off resigning of old releases) <ftpadmin@kernel.org>

The private key used for this purpose has been destroyed and cannot be
used to sign any releases produced after 2011.

