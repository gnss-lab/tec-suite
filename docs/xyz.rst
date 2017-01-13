#################
Moving receiver
#################

Change of site location (i.e. change of the values of geocentric
coordinates X, Y, Z during the file reading) is taken into account in
the calculation of elevation and azimuth values. Moreover, there is a
possibility to set the coordinates for required moments of time. To do
that, one should put a file with the values of time and geocentric
coordinates corresponding to them into a directory with an observation
file. Running into such a file, ``tecs`` will read the coordinates and
changes the values of X, Y and Z for each time moment listed in the
file.

File with coordinates
=====================

The name of a file with coordinates should correspond to the name of
an observation file and has an extension ``xyz``. For example,

- ``usud0700.11d.Z`` and ``usud0700.11d.xyz``;
- ``usud0700.11o`` and ``usud0700.11o.xyz``;
- ``usud070a00.11o`` and ``usud070a00.11o.xyz``.

Time stamp is set as ``YYYY-MM-DD HH:MM:SS`` followed by values of the
X, Y and Z (in meters) separated by spaces. The ``#`` symbol begins a
comment. For example,

::

    # Site: USUD
    # Datum: IGS08
    # datetime, x (meters), y (meters), z (meters)
    2011-03-11 05:00:00  -3855263.0771  3427432.6022  3741020.3066
    2011-03-11 05:00:30  -3855263.0833  3427432.6068  3741020.3148
    2011-03-11 05:01:00  -3855263.0761  3427432.6020  3741020.3089
    ...

