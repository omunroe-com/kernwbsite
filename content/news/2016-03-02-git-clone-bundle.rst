Cloning Linux from a bundle
===========================

:category: Site news

If you find yourself on an unreliable Internet connection and need to
perform a fresh clone of Linux.git, you may find it tricky to do so if
your connection resets before you are able to complete the clone. There
is currently no way to resume a git clone using git, but there is a neat
trick you can use instead of cloning directly -- using `git bundle`_
files.

Here is how you would do it.

1. Start with "``wget -c``", which tells wget to continue interrupted
   downloads. If your connection resets, just rerun the same command while
   in the same directory, and it will pick up where it left off::

     wget -c https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/clone.bundle

2. Once the download is completed, verify that the bundle has downloaded
   correctly::

     git bundle verify clone.bundle
     ...
     clone.bundle is okay

3. Next, clone from the bundle::

     git clone clone.bundle linux

4. Now, point the origin to the live git repository and get the latest changes::

     cd linux
     git remote remove origin
     git remote add origin https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
     git pull origin master

Once this is done, you can delete the "``clone.bundle``" file, unless
you think you will need to perform a fresh clone again in the future.

The "``clone.bundle``" files are generated weekly on Sunday, so they
should contain most objects you need, even during kernel merge windows
when there are lots of changes committed daily.

.. _`git bundle`: https://git-scm.com/docs/git-bundle
