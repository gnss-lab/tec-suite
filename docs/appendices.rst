##########
Appendices
##########

*********
Constants
*********

List and meaning of the constants which are used for calculation.

- Conversion of geocentric coordinates into geodesic coordinates:

  - ellipsoid semi-major axis: :math:`6378137, m`;
  - ellipsoid semi-minor axis: :math:`6356752.314245, m`.

- Calculation of elevation and azimuth:

  - Earth's radius: :math:`6371 \cdot 10^3, m`.

- Calculation of geocentric coordinates of the GPS, GLONASS and GEO satellites:

  - Earth's angular velocity: :math:`7.2921151467 \cdot 10^{-5}, rad/s`;
  - Earth's gravitational field constant: :math:`39860044 \cdot 10^7, m^3/s^2`;
  - second zonal harmonic of geopotential expansion into a series of spherical functions: :math:`1082625.7 \cdot 10^{-9}`;
  - ellipsoid semi-major axis: :math:`6378136, m` (for GLONASS, according to PZ-90).

.. _sat-system-id:

****************************
Satellite system identifiers
****************************

The following is the list of the satellites system identifiers
according to the RINEX format [RNX]_:

- ``G`` - GPS
- ``R`` - GLONASS
- ``E`` - Galileo
- ``S`` - SBAS
- ``C`` - BeiDou
