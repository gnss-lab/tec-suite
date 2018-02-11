#########
tec-suite
#########

********
Overview
********

**tec-suite** is a tool for reconstruction of the slant total electron
content (TEC) value in the ionosphere. It uses data of Global
Navigation Satellite Systems such as GPS and GLONASS.  To determine
TEC value along "receiver-satellite" line-of-sight, **tec-suite** uses
phase and pseudorange derived from RINEX files [RNX]_.

For the moment **tec-suite** supports:

* Navigation systems:

  * GPS
  * GLONASS
  * Galileo
  * Compass/BeiDou
  * GEO (geostationary satellites, part of `SBAS`_)
  * IRNSS

.. _SBAS: http://www.navipedia.net/index.php/SBAS
     
* RINEX versions:

  * v.2 (2.0 - 2.11)
  * v.3 (3.0 - 3.03)

* File types:

  * RINEX observation files
  * Hatanaka-compressed RINEX observation files [CRNX]_
  * RINEX navigation files
  * compressed (.Z or .gz) files

********
Contents
********

.. toctree::
   :maxdepth: 2

   installation
   usage
   xyz
   appendices
   bibliography
