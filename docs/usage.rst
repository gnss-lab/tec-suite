#####
Usage
#####

********
Synopsis
********

**tec-suite** is a command line tool. There is an executable named
``tecs`` (or ``tecs.exe``) you should invoke to make work done.

In general, the command line looks like:

``tecs [-v] [-c config_file] [--save-coordinates]``

************
Command line
************

All the arguments are optional.

``-c file``
    Use the given config file instead of ``tecs.cfg``.

``-v``
    Print the version and exit.

``--save-coordinates``
    Save the coordinates of the sites found in ``obsDir`` into
    ``coordinates.txt``. TEC values are not calculated, the file is
    saved in a directory which contains configuration file.

*************
Configuration
*************

The configuration file contains a set of variables that affect the
``tecs`` behaviour. If not set explicitly with ``-c file``, ``tecs``
will look for ``tecs.cfg`` in the working dir.

The syntax is simple; white-spaces are ignored, the ``#`` symbol begins
comment to the end of the line, blank lines are ignored. All other
lines are identified as setting variables, in the form ``name =
value``. The variable names are case sensitive.


.. _variables:

Variables
=========

``obsDir`` *dir [, dir, ...]*
    Directory with the RINEX observation files. It can contain a list
    of the directories separated by a comma.

``navDir``  *dir [, dir, ...]*
    Directory with the RINEX navigation files. It can contain a list
    of the directories separated by a comma.

``outDir`` *dir*
    Output directory; output files will be saved in it.

``outFileMode`` *mode*
    Output file format. The only one format available by now, and it
    is the ``text`` format (``outFileMode = text``). Output data will
    be saved in multicolumn text files. The set and the order of data
    columns are defined by the ``recFields`` variable.

``recFields`` *'rec format'*
    Set and order of output file columns. A complete list of the
    columns ("fields") is given in the :ref:`out-file` section.

``datetimeFormat`` *'date format'*
    Date/time format in output file; see the :ref:`datetime` section
    for details.

``samplingInterval`` *seconds*
    Interval in seconds to pick values from an observation
    file. Values of TEC, azimuth and elevation will be calculated with
    the interval. In case of ``samplingInterval = 0`` all the data
    will be read. 

``navPriorityGPS`` *site*\ :sub:`1`\ , *site*\ :sub:`2`\ , ..., *site*\ :sub:`N`
    Priority of search of navigation files for GPS. Here, *site* is a
    4-symbol code of the station (the first 4 symbols of RINEX file
    name). First, ``tecs`` searches for *site*\ :sub:`1` navigation
    file. If it does not find it, it searches for *site*\ :sub:`2`
    file and so on to *site*\ :sub:`N`. If ``tecs`` does not find any
    navigation file from the list, it takes the first available file.
    
``navPriorityGLO`` *site*\ :sub:`1`\ , *site*\ :sub:`2`\ , ..., *site*\ :sub:`N`
    It is an analogue of ``navPriorityGPS`` for GLONASS.

``navPriorityGEO`` *site*\ :sub:`1`\ , *site*\ :sub:`2`\ , ..., *site*\ :sub:`N`
    It is an analogue of ``navPriorityGPS`` for SBAS.

``navIgnoreAbsence`` [True|False]
    When ``True``, absence of navigation files for all satellite
    systems besides GLONASS is ignored. The values of elevation and
    azimuth are not calculated and are written as ``0``. Note that for
    GLONASS the navigation file is required to calculate frequencies.

``logLevel`` (DEBUG|INFO|WARNING|ERROR|CRITICAL)
   Sets the logging level. ``ERROR`` is usually enough. 

.. _out-file:

Output file
-----------

The results are written into multicolumn text files. The name of an
output file is formed as follows:

``site_SN_DDD_YY.dat``, where

*site* - site name, *S* - :ref:`satellite system identifier
<sat-system-id>`, *N* - satellite number, *DDD* - day of the
year, *YY* - year without century.

The order and the set of the output record fields are set by the
``recFields`` variable.  The ``recFields`` value is a single quoted
string which contains field names separated by a comma. For example,

``recFields = 'datetime, el, az, tec.l1l2, tec.p1p2'``

Therefore, it is possible to set the format of an output record so that it
contains only desired values. The field names listed in
:ref:`table-tec` and :ref:`table-other`.

The following is the list of TEC reconstruction variants, which values can
be written into an output file.

.. _table-tec:

.. table:: The TEC fields list
   	   
   +------------+--------------------------------------------------------------------+
   | Notation   | Meaning                                                            |
   +============+====================================================================+
   | tec.p1p2   | TEC value reconstructed using pseudorange P1 and P2 values         |
   +------------+--------------------------------------------------------------------+
   | tec.c1p2   | The same but using C1 and P2 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.c1c2   | The same but using C1 and C2 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.c1c5   | The same but using C1 and C5 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.c2c5   | The same but using C2 and C5 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.c2c6   | The same but using C2 and C6 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.c2c7   | The same but using C2 and C7 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.c6c7   | The same but using C6 and C7 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.l1l2   | TEC value reconstructed using phase L1 and L2 values               |
   +------------+--------------------------------------------------------------------+
   | tec.l1l5   | The same but using L1 and L2 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.l2l5   | The same but using L2 and L5 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.l2l6   | The same but using L2 and L6 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.l2l7   | The same but using L2 and L7 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.l6l7   | The same but using L6 and L7 values                                |
   +------------+--------------------------------------------------------------------+
   | tec.l1c1   | TEC value reconstructed using phase L1 and pseudorange C1 values   |
   +------------+--------------------------------------------------------------------+ 
   | tec.l2c2   | TEC value reconstructed using phase L2 and pseudorange C2 values   |
   +------------+--------------------------------------------------------------------+ 

The following is the list of other fields which can be inserted
into ``recFields`` variable.

.. _table-other:

.. table:: The output fields list
   
   +----------+-----------------------------------------------------------------------+
   | Notation | Meaning                                                               |
   +==========+=======================================================================+
   |                                 *Date and time*                                  |
   +----------+-----------------------------------------------------------------------+
   | tsn      |Time of the observation :math:`t_{sn} = sec/dt`, where :math:`sec` -   |
   |          |number of seconds from the beginning of the day, :math:`dt` - the      |
   |          |observation interval in seconds.                                       |
   +----------+-----------------------------------------------------------------------+
   | hour     |Time of the observation in fractions of an hour.                       |
   +----------+-----------------------------------------------------------------------+
   | datetime |Date and time of the observation. You can control date/time string     |
   |          |using the ``datetimeFormat`` variable (see :ref:`datetime` section).   |
   +----------+-----------------------------------------------------------------------+
   |                                  *Coordinates*                                   |
   +----------+-----------------------------------------------------------------------+
   |  site.x  |Geocentric coordinate :math:`X` of a receiver.                         |
   +----------+-----------------------------------------------------------------------+
   | site.y   |Geocentric coordinate :math:`Y` of a receiver.                         |
   +----------+-----------------------------------------------------------------------+
   | site.z   |Geocentric coordinate :math:`Z` of a receiver.                         |
   +----------+-----------------------------------------------------------------------+
   | site.l   |Geographic longitude :math:`L` of a receiver.                          |
   +----------+-----------------------------------------------------------------------+
   | site.b   |Geographic latitude :math:`B` of a receiver.                           |
   +----------+-----------------------------------------------------------------------+
   | site.h   |Altitude :math:`B` of a receiver.                                      |
   +----------+-----------------------------------------------------------------------+
   | sat.x    |Geocentric coordinate :math:`X` of a satellite.                        |
   +----------+-----------------------------------------------------------------------+
   | sat.y    |Geocentric coordinate :math:`Y` of a satellite.                        |
   +----------+-----------------------------------------------------------------------+
   | sat.z    |Geocentric coordinate :math:`Z` of a satellite.                        |
   +----------+-----------------------------------------------------------------------+
   | el       |Elevation to a satellite.                                              |
   +----------+-----------------------------------------------------------------------+
   | az       |Azimuth to a satellite.                                                |
   +----------+-----------------------------------------------------------------------+
   |                               *Observable values*                                |
   +----------+-----------------------------------------------------------------------+
   | p1       |P1 pseudorange value.                                                  |
   +----------+-----------------------------------------------------------------------+
   | p2       |P2 pseudorange value.                                                  |
   +----------+-----------------------------------------------------------------------+
   | l1       |L1 carrier phase value.                                                |
   +----------+-----------------------------------------------------------------------+
   | l2       |L2 carrier phase value.                                                |
   +----------+-----------------------------------------------------------------------+
   | l5       |L5 carrier phase value.                                                |
   +----------+-----------------------------------------------------------------------+
   | s1       |S1 raw signal strength value.                                          |
   +----------+-----------------------------------------------------------------------+
   | s2       |S2 raw signal strength value.                                          |
   +----------+-----------------------------------------------------------------------+
   | s5       |S5 raw signal strength value.                                          |
   +----------+-----------------------------------------------------------------------+
   | c1       |С1 pseudorange value.                                                  |
   +----------+-----------------------------------------------------------------------+
   | c2       |С2 pseudorange value.                                                  |
   +----------+-----------------------------------------------------------------------+
   | c5       |C5 pseudorange value.                                                  |
   +----------+-----------------------------------------------------------------------+
   | p1.lli   |P1 Loss of Lock Indicator (LLI) value.                                 |
   +----------+-----------------------------------------------------------------------+
   | p2.lli   |P2 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | l1.lli   |L1 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | l2.lli   |L2 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | l5.lli   |L5 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | s1.lli   |S1 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | s2.lli   |S2 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | s5.lli   |S5 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | c1.lli   |C1 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | c2.lli   |C2 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+
   | c5.lli   |C5 LLI.                                                                |
   +----------+-----------------------------------------------------------------------+

.. _datetime:

Date/time
----------

Using the ``datetimeFormat`` variable one can set the format of the
``datetime`` field which will be written into an output file. Note
that the ``datetime`` field should be put into the ``recFields``
string.

The ``datetimeFormat`` string can include:

- any printable character;
- date/time codes (according to the С standard 1989 version).

For example, ``%Y-%m-%d %H:%M:%S`` corresponds to ``2015-06-23 12:00:00``.
The following is the list of codes.

====    =======
Code    Meaning
====    =======
%a      Weekday as locale’s abbreviated name.
%A      Weekday as locale’s full name.
%w      Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.
%d      Day of the month as a zero-padded decimal number.
%b      Month as locale’s abbreviated name.
%B      Month as locale’s full name.
%m      Month as a zero-padded decimal number.
%y      Year without century as a zero-padded decimal number.
%Y      Year with century as a decimal number.
%H      Hour (24-hour clock) as a zero-padded decimal number.
%I      Hour (12-hour clock) as a zero-padded decimal number.
%p      Locale’s equivalent of either AM or PM.
%M      Minute as a zero-padded decimal number.
%S      Second as a zero-padded decimal number.
%f      Microsecond as a decimal number, zero-padded on the left.
%z      UTC offset in the form +HHMM or -HHMM (empty string if the object is naive).
%Z      Time zone name (empty string if the object is naive).
%j      Day of the year as a zero-padded decimal number.
%U      Week number of the year (Sunday as the first day of the week) 
        as a zero padded decimal number. All days in a new year preceding
        the first Sunday are considered to be in week 0.
%W      Week number of the year (Monday as the first day of the week)
        as a decimal number. All days in a new year preceding the 
        first Monday are considered to be in week 0.
%c      Locale’s appropriate date and time representation.
%x      Locale’s appropriate date representation.
%X      Locale’s appropriate time representation.
%%      A literal '%' character.
====    =======
