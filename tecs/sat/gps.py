#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2017 Ilya Zhivetiev <i.zhivetiev@gnss-lab.org>
#
# This file is part of tec-suite.
#
# tec-suite is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tec-suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tec-suite.  If not, see <http://www.gnu.org/licenses/>.

""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from math import sin, cos, atan2, sqrt

from tecs.sat import datum

# start of the GPS epoch
epoch_start = datetime.datetime(1980, 1, 6, 0, 0, 0)

# frequencies, Hz
F1 = 1575.42 * 1e6
F2 = 1227.60 * 1e6
F5 = 1176.45 * 1e6


def compute_sat_xyz(ephemeris, sec):
    """compute_sat_xyz(ephemeris, sec) -> (x, y, z)

    calculates geocentric coordinate of the satellite X, Y, Z.

    Parameters
    ----------
    ephemeris : list
        list with ephemeris

    sec : float
        amount of seconds since the start of the week, seconds

    Returns
    -------
    x : float
        X, meters
    y : float
        Y, meters
    z : float
        Z, meters
    """
    # threshold
    # e_ps = 2e-15

    crs = ephemeris[1]
    dn = ephemeris[2]
    m0 = ephemeris[3]
    cuc = ephemeris[4]
    e0 = ephemeris[5]
    cus = ephemeris[6]
    a0 = ephemeris[7] ** 2
    toe = ephemeris[8]
    cic = ephemeris[9]
    omega_0 = ephemeris[10]
    cis = ephemeris[11]
    i0 = ephemeris[12]
    crc = ephemeris[13]
    w0 = ephemeris[14]
    omega_dot = ephemeris[15]
    i_dot = ephemeris[16]

    tk = sec - toe

    if tk > 302400:
        tk -= 604800
    elif tk < -302400:
        tk += 604800

    n = sqrt(datum.mu / a0 ** 3) + dn
    mk = m0 + n * tk

    ek = mk
    ek_1 = ek + 1

    prv_d_ek = 0
    cur_d_ek = 1
    #   while ( abs(ek-ek_1) > e_ps ):
    while prv_d_ek != cur_d_ek:
        prv_d_ek = abs(ek - ek_1)
        ek_1 = ek
        ek = ek_1 - (ek_1 - e0 * sin(ek_1) - mk) / (1 - e0 * cos(ek_1))
        cur_d_ek = abs(ek - ek_1)
        # print prv_d_ek, cur_d_ek

    fs = (sqrt(1 - e0 ** 2) * sin(ek)) / (1 - e0 * cos(ek))
    fc = (cos(ek) - e0) / (1 - e0 * cos(ek))
    tettak = atan2(fs, fc)

    u0k = tettak + w0
    uk = u0k + cuc * cos(2 * u0k) + cus * sin(2 * u0k)

    rk = a0 * (1 + e0 * cos(ek)) + crc * cos(2 * u0k) + crs * sin(2 * u0k)

    ik = i0 + (cic * cos(2 * u0k) + cis * sin(2 * u0k)) + i_dot * tk

    omega_k = omega_0 + (omega_dot - datum.omega) * tk - datum.omega * toe

    x = rk * (cos(uk) * cos(omega_k) - sin(uk) * sin(omega_k) * cos(ik))
    y = rk * (cos(uk) * sin(omega_k) + sin(uk) * cos(omega_k) * cos(ik))
    z = rk * sin(uk) * sin(ik)

    return x, y, z
