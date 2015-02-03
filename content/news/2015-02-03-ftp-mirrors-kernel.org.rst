FTP limited on mirrors.kernel.org
=================================

:category: Site news
:author: Konstantin Ryabitsev

We've had to temporarily limit FTP access to mirrors.kernel.org due
to high IO load.

We have recently upgraded our hardware in order to increase capacity --
16TB was no longer nearly sufficient enough to host all the distro
mirrors and archives. We chose larger but slower disks and offset the
loss of performance by heavily utilizing SSD IO caching using dm-cache.

While it was performing very well, we have unfortunately run across an
FS data corruption bug somewhere along this stack::

    megaraid_sas + dm_cache + libvirt/virtio + xfs

We've temporarily removed dm-cache from the picture and switched to
Varnish on top of SSD for http object caching. Unfortunately, as Varnish
does not support FTP, we had to restrict FTP protocol to a limited
number of concurrent sessions in order to reduce disk IO. If you are
affected by this, simply switch to HTTP protocol that does not have such
restrictions.

This is a temporary measure until we identify the dm-cache problem that
was causing data corruption, at which point we will restore unrestricted
FTP access.
