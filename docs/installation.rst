############
Installation
############

Just download and extract **tec-suite** archive wherever you want.

Downloads:

* `Windows <http://somewhere.com>`_
* `Linux <http://somewhere.com>`_
* `macOS <http://somewhere.com>`_

************
Requirements
************

``crx2rnx``
    To decompress Hatanaka-compressed RINEX files, **tec-suite** uses
    `crx2rnx <http://terras.gsi.go.jp/ja/crx2rnx.html>`_.

``gunzip``
    To unarchive ``.z``, ``.Z`` or ``.gz``, files **tec-sutie**
    uses ``gunzip``. If your system is **Linux** or **macOS** you
    probably have it installed. You can find the **Windows** version
    at `GnuWin <http://gnuwin32.sourceforge.net/packages/gzip.htm>`_
    site.

.. note::

   Put ``crx2rnx`` (and ``gunizp`` if you're running Windows) to a dir
   where ``tecs`` could find it, e.g. to the dir which contains
   ``tecs`` binary or to any dir in ``$PATH`` variable.
