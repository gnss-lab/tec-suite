tec-suite v0.7.4
----------------

Software to reconstruct slant total electron content (TEC) value in
the ionosphere using data derived from global navigation satellite
systems such as GPS, GLONASS, etc.

Features
========

For the moment **tec-suite** supports:

* Navigation systems:

  * GPS
  * GLONASS
  * Galileo
  * Compass/BeiDou
  * GEO

* RINEX versions:

  * v2 (2.0 - 2.11)
  * v3 (3.0 - 3.03)

* File types:

  * RINEX observation files
  * Hatanaka-compressed RINEX observation files
  * RINEX navigation files
  * compressed (.Z or .gz) files

Documentation
=============

You can find the documentation at readthedocs.io_ site.

.. _readthedocs.io: http://tec-suite.readthedocs.io

Installation
============

Just download and extract **tec-suite** archive wherever you want.

Downloads
~~~~~~~~~

* `Windows <http://somewhere.com>`_
* `Linux <http://somewhere.com>`_
* `macOS <http://somewhere.com>`_

To install **tec-suite** manually:

pip ...

Requirements
~~~~~~~~~~~~

``crx2rnx``
    To decompress Hatanaka-compressed RINEX files, **tec-suite** uses
    `crx2rnx <http://terras.gsi.go.jp/ja/crx2rnx.html>`_.

``gunzip``
    To unarchive ``.z``, ``.Z`` or ``.gz``, files **tec-suite**
    uses ``gunzip``. If your system is **Linux** or **macOS** you
    probably have it installed. You can find the **Windows** version
    at `GnuWin <http://gnuwin32.sourceforge.net/packages/gzip.htm>`_
    site.

Usage
=====

* Edit ``tecs.cfg``
* Run ``tecs`` (or ``tecs.exe``)

For further details see `the documentation`__.

__ readthedocs.io_

Bugs
====

Report any bugs via project's `issue tracker <http://github.com>`_.
Feel free to fork and play with the code. I will appreciate fixes
and suggestions.

License
=======

Copyright (c) 2017 Ilya Zhivetiev <i.zhivetiev@gnss-lab.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
