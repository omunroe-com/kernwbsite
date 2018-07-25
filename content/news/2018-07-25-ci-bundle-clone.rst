Best way to do linux clones for your CI
=======================================

:category: Site news

If you are in charge of CI infrastructure that needs to perform frequent
full clones of kernel trees from git.kernel.org, we strongly recommend
that you use the `git bundles we provide`_ instead of performing a full
clone directly from git repositories.

It is better for you, because downloading the bundle from CDN is
probably going to be much faster for you than cloning from our frontends
due to the CDN being more local. You can even copy the bundle to a
fileserver on your local infrastructure and save a lot of repeated
external traffic.

It is better for us, because if you first clone from the bundle, you
only need to fetch a handful of newer objects directly from
git.kernel.org frontends. This not only uses an order of magnitude less
bandwidth, but also results in a much smaller memory footprint on our
systems -- git daemon needs a lot of RAM when serving full clones of
linux repositories.

Here is a simple script that will help you automate the process of first
downloading the git bundle and then fetching the newer objects:

- `linux-bundle-clone`_

Thank you for helping us keep our systems fast and accessible to all.

.. _`git bundles we provide`: https://www.kernel.org/cloning-linux-from-a-bundle.html
.. _`linux-bundle-clone`: https://git.kernel.org/pub/scm/linux/kernel/git/mricon/korg-helpers.git/plain/linux-bundle-clone
