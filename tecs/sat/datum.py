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

""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from math import sqrt

# WGS84 values

# semiaxis of the ellipse
a = 6378137.00
b = 6356752.314245

# eccentricity of the ellipse
e = sqrt(1 - pow(b, 2)/pow(a, 2))
# e = 0.081819199

# radius of the Earth
r_e = 6371e3

# m^3/s^2 - Earth's gravitational field constant
mu = 398600.44e+9

# equatorial radius of the Earth
ae = 6378136  # ПЗ-90 (ICD GLONASS)

# second zonal harmonic of the spherical harmonic
J0sqd = 1082625.7e-9

# second zonal harmonic coefficient
C20 = -1082.63e-6

# angular velocity of the Earth, rad/sec
omega = 7.2921151467e-5
