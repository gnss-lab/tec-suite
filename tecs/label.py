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

"""labels used in the tecs configuration
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# outfile types
OUT_FILE_TEXT = 'text'

# TEC labels
R_TEC_ALL = []

R_TEC_L1L2 = 'tec.l1l2'
R_TEC_ALL.append(R_TEC_L1L2)

R_TEC_L1L5 = 'tec.l1l5'
R_TEC_ALL.append(R_TEC_L1L5)

R_TEC_L2L5 = 'tec.l2l5'
R_TEC_ALL.append(R_TEC_L2L5)

R_TEC_P1P2 = 'tec.p1p2'
R_TEC_ALL.append(R_TEC_P1P2)

R_TEC_C1P2 = 'tec.c1p2'
R_TEC_ALL.append(R_TEC_C1P2)

R_TEC_C1C2 = 'tec.c1c2'
R_TEC_ALL.append(R_TEC_C1C2)

R_TEC_C1C5 = 'tec.c1c5'
R_TEC_ALL.append(R_TEC_C1C5)

R_TEC_C2C5 = 'tec.c2c5'
R_TEC_ALL.append(R_TEC_C2C5)

R_TEC_L1C1 = 'tec.l1c1'
R_TEC_ALL.append(R_TEC_L1C1)

R_TEC_L2C2 = 'tec.l2c2'
R_TEC_ALL.append(R_TEC_L2C2)

R_TEC_L8C8 = 'tec.l8c8'
R_TEC_ALL.append(R_TEC_L8C8)

R_TEC_L2L6 = 'tec.l2l6'
R_TEC_ALL.append(R_TEC_L2L6)

R_TEC_L2L7 = 'tec.l2l7'
R_TEC_ALL.append(R_TEC_L2L7)

R_TEC_L6L7 = 'tec.l6l7'
R_TEC_ALL.append(R_TEC_L6L7)

R_TEC_C2C6 = 'tec.c2c6'
R_TEC_ALL.append(R_TEC_C2C6)

R_TEC_C2C7 = 'tec.c2c7'
R_TEC_ALL.append(R_TEC_C2C7)

R_TEC_C6C7 = 'tec.c6c7'
R_TEC_ALL.append(R_TEC_C6C7)

R_TEC_ALL = tuple(R_TEC_ALL)

# format labels
R_ALL = 'all'

R_TSN = 'tsn'
R_HOUR = 'hour'
R_DATETIME = 'datetime'

R_ELEVATION = 'el'
R_AZIMUTH = 'az'

R_VALIDITY = 'validity'

R_P1 = 'p1'
R_P1_LLI = 'p1.lli'
R_P2 = 'p2'
R_P2_LLI = 'p2.lli'

R_L1 = 'l1'
R_L1_LLI = 'l1.lli'
R_L2 = 'l2'
R_L2_LLI = 'l2.lli'
R_L5 = 'l5'
R_L5_LLI = 'l5.lli'

R_S1 = 's1'
R_S1_LLI = 's1.lli'
R_S2 = 's2'
R_S2_LLI = 's2.lli'
R_S5 = 's5'
R_S5_LLI = 's5.lli'

R_C1 = 'c1'
R_C1_LLI = 'c1.lli'
R_C2 = 'c2'
R_C2_LLI = 'c2.lli'
R_C5 = 'c5'
R_C5_LLI = 'c5.lli'

R_SAT_X = 'sat.x'
R_SAT_Y = 'sat.y'
R_SAT_Z = 'sat.z'

R_SITE_X = 'site.x'
R_SITE_Y = 'site.y'
R_SITE_Z = 'site.z'

R_SITE_L = 'site.l'
R_SITE_B = 'site.b'
R_SITE_H = 'site.h'
