#!/usr/bin/env python
# coding=utf8
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

"""Common satellite system functions
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from math import pi, sin, cos, atan, atan2, sqrt

from tecs.sat import datum

NAME = 'tecs.sat.common'


# noinspection PyPep8Naming
def xyz2lbh(x, y, z):
    """xyz2lbh_deg(x, y, z) -> (l, b, h)

    cartesian to geodetic coordinates conversion.

    Parameters
    ----------
    x, y, z : float
        meters

    Returns
    -------
    l, b : float
        longitude and latitude, radians

    h : float
        height, meters

    Note
    ----
    К.Ф. Афонин Высшая геодезия. Системы координат и преобразования
        между ними // Новосибирск. СГГА. 2011 г. 55 с.
    """

    datum_e = datum.e
    datum_a = datum.a

    # threshold
    e_B = 1e-12

    Q = sqrt(x ** 2 + y ** 2)

    # L - longitude
    if x == 0:
        if y > 0:
            L = pi / 2
        else:
            L = 3 * pi / 2
    else:
        L = atan2(y, x)

    # B - latitude
    # initial values
    Bi1 = z / Q * 1 / (1 - datum_e ** 2)
    Bi = Bi1
    N = 0

    while 1:
        W = sqrt(1 - datum_e ** 2 * sin(Bi) ** 2)
        N = datum_a / W
        T = z + N * datum_e ** 2 * sin(Bi)

        Bi1 = atan2(T, Q)

        if abs(Bi1 - Bi) <= e_B:
            break

        Bi = Bi1

    B = Bi1

    # H - height
    H = Q * cos(B) + z * sin(B) - N * (1 - datum_e ** 2 * sin(B) ** 2)

    return L, B, H


def compute_el_az(obs, sat):
    """compute_el_az(obs, sat) -> el, az

    computes elevation and azimuth to satellite.

    Parameters
    ----------
    obs : tuple
        obs = (x, y, z); cartesian coordinates of the observer

    sat : tuple
        sat = (x, y, z); cartesian coordinates of the satellite

    Returns
    -------
    el : float
        elevation, deg
    az : float
        azimuth, deg
    """

    datum_re = datum.r_e

    (x_0, y_0, z_0) = obs
    (x_s, y_s, z_s) = sat

    (l_0, b_0) = xyz2lbh(*obs)[0:2]
    (l_s, b_s) = xyz2lbh(*sat)[0:2]

    r_k = sqrt(x_s ** 2 + y_s ** 2 + z_s ** 2)

    sigma = atan(
        sqrt(1 - (
            sin(b_0) * sin(b_s) + cos(b_0) * cos(b_s) * cos(l_s - l_0)) ** 2)
        / (sin(b_0) * sin(b_s) + cos(b_0) * cos(b_s) * cos(l_s - l_0))
    )

    x_t = -(x_s - x_0) * sin(l_0) + (y_s - y_0) * cos(l_0)
    y_t = (-(x_s - x_0) * cos(l_0) * sin(b_0) -
           (y_s - y_0) * sin(l_0) * sin(b_0) + (z_s - z_0) * cos(b_0))

    el = atan((cos(sigma) - datum_re / r_k) / sin(sigma))
    az = atan2(x_t, y_t)

    el *= 180 / pi
    az *= 180 / pi

    # 0 - 360
    if az < 0:
        az += 360

    return el, az


def xyz2lbh_deg(x, y, z):
    """warp for xyz2lbg()
    """
    logger = logging.getLogger(NAME + '.xyz2lbh_deg')

    try:
        (l, b, h) = xyz2lbh(x, y, z)

    except ArithmeticError as err:
        msg = ("Can't calculate LBH values: %s, XYZ = (%s, %s, %s)." %
               (err, x, y, z))
        logger.error(msg)
        return 0, 0, 0

    (l, b) = l * 180 / pi, b * 180 / pi

    if l < 0:
        l += 360

    return l, b, h
