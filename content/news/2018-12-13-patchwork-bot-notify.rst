Get notifications for your patches
==================================

:category: Site news

We are trialing out a new feature that can send you a notification when
the patches you send to the LKML are applied to linux-next or to the
mainline git trees. If you are interested in trying it out, here are the
details:

- The patches must be sent to the LKML (linux-kernel@vger.kernel.org).
- One of the cc's must be notify@kernel.org (Bcc will not work).
- Alternatively, there should be a "X-Patchwork-Bot: notify" email header.
- The patches must not have been modified by the maintainer(s).
- All patches in the series must have been applied, not just some of them.

The last two points are important, because if there are changes between
the content of the patch as it was first sent to the mailing list, and
how it looks like by the time it is applied to linux-next or mainline,
the bot will not be able to recognize it as the same patch. Similarly,
for series of multiple patches, the bot must be able to successfully
match all patches in the series in order for the notification to go out.

If you are using ``git-format-patch``, it is best add the special header
instead of using the Cc notification address, so as to avoid any
unnecessary email traffic::

    --add-header="X-Patchwork-Bot: notify"

You should receive one notification email per each patch series, so if
you send a series of 20 patches, you will get a single email in the form
of a reply to the cover letter, or to the first patch in the series. The
notification will be sent directly to you, ignoring any other addresses
in the Cc field.

The bot uses our `LKML patchwork instance`_ to perform matching and
tracking, and the `source code`_ for the bot is also available if you
would like to suggest improvements.

.. _`LKML patchwork instance`: https://lore.kernel.org/patchwork
.. _`source code`: https://git.kernel.org/pub/scm/linux/kernel/git/mricon/korg-helpers.git/tree/git-patchwork-bot.py
