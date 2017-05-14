If you got "BAD Signature" this morning
=======================================

:category: Site news

The XZ tarballs for the following kernel releases did not initially pass
signature verification due to benign changes to the tarball structure
done by the pixz compression tool:

- 4.11.1
- 4.10.16
- 4.9.28
- 4.4.68

These changes would have resulted in GPG returning "Bad Signature" if
you tried to verify their integrity. Once we identified the problem, we
generated new XZ tarballs without tar header modifications and now they
should all pass PGP signature verification.

We preserved the original .xz tarballs as -badsig files in the archives
in case you wanted to verify that there was nothing malicious in them,
merely tar header changes. You can find them in the same v4.x directory:

- https://www.kernel.org/pub/linux/kernel/v4.x/

Our apologies for this problem.

Regards,
Konstantin
