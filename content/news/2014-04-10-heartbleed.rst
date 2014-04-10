Heartbleed statement
====================

:category: Site news
:author: Konstantin Ryabitsev

Since we rely on the OpenSSL library for serving most of our websites,
we, together with most of the rest of the open-source world, were
vulnerable to the HeartBleed_ vulnerability. We have switched to the
patched version of OpenSSL within hours of it becoming available, plus
have performed the following steps to mitigate any sensitive information
leaked via malicious SSL heartbeat requests:

* Replaced all SSL keys across all kernel.org sites.
* Expired all active sessions on Bugzilla, Patchwork, and Mediawiki
  sites, requiring everyone to re-login.
* Changed all passwords used for admin-level access to the above sites.

As kernel.org developers do not rely on SSL to access git repositories,
there is no need to replace any SSH or PGP keys used for developer
authentication.

If you have any questions or concerns, please email us at
webmaster@kernel.org for more information.

.. _HeartBleed: http://heartbleed.com/
