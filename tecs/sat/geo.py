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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import sqrt
from tecs.sat import datum

# frequencies, Hz
F1 = 1575.42 * 1e6
F5 = 1176.45 * 1e6


# noinspection PyPep8Naming,PyShadowingNames
def compute_sat_xyz(eph, dt):
    """compute_sat_xyz(eph, dt) -> (x, y, z)

    calculates geocentric coordinate of the satellite X, Y, Z

    Parameters
    ----------
    eph : list
        list with ephemeris

    dt : float
        difference between time of the ephemeris and observation time, seconds

    Returns
    -------
    x : float
        X, meters
    y : float
        Y, meters
    z : float
        Z, meters
    """

    # meters
    x0 = eph[0] * 1000
    vX = eph[1] * 1000
    aX = eph[2] * 1000

    y0 = eph[4] * 1000
    vY = eph[5] * 1000
    aY = eph[6] * 1000

    z0 = eph[8] * 1000
    vZ = eph[9] * 1000
    aZ = eph[10] * 1000

    if dt == 0:
        return x0, y0, z0

    r = sqrt(x0 ** 2 + y0 ** 2 + z0 ** 2)

    # - GLONASS ICD ver 5.1, 2008.
    first_sd = -(datum.mu / r ** 3)
    second_sd = 3 / 2. * datum.J0sqd * datum.mu * datum.ae ** 2 / r ** 5

    # noinspection PyPep8
    fx = lambda x, z: (first_sd * x - second_sd * x *
                       (1 - 5 * z ** 2 / r ** 2) +
                       datum.omega ** 2 * x + 2 * datum.omega * vY + aX)

    # noinspection PyPep8
    fy = lambda y, z: (first_sd * y - second_sd * y *
                       (1 - 5 * z ** 2 / r ** 2) +
                       datum.omega ** 2 * y - 2 * datum.omega * vX + aY)

    # noinspection PyPep8
    fz = lambda z: (first_sd * z - second_sd * z *
                    (3 - 5 * z ** 2 / r ** 2) + aZ)

    x = dict()
    kx = dict()

    y = dict()
    ky = dict()

    z = dict()
    kz = dict()

    # 1
    kx[1] = fx(x0, z0) * dt
    ky[1] = fy(y0, z0) * dt
    kz[1] = fz(z0) * dt

    x[1] = x0 + vX * dt / 2. + kx[1] * dt / 8.
    y[1] = y0 + vY * dt / 2. + ky[1] * dt / 8.
    z[1] = z0 + vZ * dt / 2. + kz[1] * dt / 8.

    # 2
    kx[2] = fx(x[1], z[1]) * dt
    ky[2] = fy(y[1], z[1]) * dt
    kz[2] = fz(z[1]) * dt

    x[2] = x0 + vX * dt / 2. + kx[2] * dt / 8.
    y[2] = y0 + vY * dt / 2. + ky[2] * dt / 8.
    z[2] = z0 + vZ * dt / 2. + kz[2] * dt / 8.

    # 3
    kx[3] = fx(x[2], z[2]) * dt
    ky[3] = fy(y[2], z[2]) * dt
    kz[3] = fz(z[2]) * dt

    # result
    xyz = (
        x0 + vX * dt + (kx[1] + kx[2] + kx[3]) * dt / 6,
        y0 + vY * dt + (ky[1] + ky[2] + ky[3]) * dt / 6,
        z0 + vZ * dt + (kz[1] + kz[2] + kz[3]) * dt / 6
    )

    return xyz
