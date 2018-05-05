############
Installation
############

Just download and extract **tec-suite** archive wherever you want.

Downloads:

* `Windows <https://github.com/gnss-lab/tec-suite/releases/download/v0.7.8/tec-suite-v0.7.8-win32.zip>`_
* Linux: x86_32_ and x86_64_
* `macOS <https://github.com/gnss-lab/tec-suite/releases/download/v0.7.8/tec-suite-v0.7.8-macos.tgz>`_

.. _x86_32: https://github.com/gnss-lab/tec-suite/releases/download/v0.7.8/tec-suite-v0.7.8-linux32.tgz
.. _x86_64: https://github.com/gnss-lab/tec-suite/releases/download/v0.7.8/tec-suite-v0.7.8-linux64.tgz


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

   **tec-suite** for Windows comes with ``crx2rnx`` and ``gzip`` executables. In
   case of Linux or macOS put ``crx2rnx`` to a dir where ``tecs`` could find it,
   e.g. to the dir which contains ``tecs`` binary or to any dir in ``$PATH``
   variable.
