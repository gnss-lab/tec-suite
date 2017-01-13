#!/usr/bin/env python
# coding: utf8
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

"""
Collection of labels of the different RINEX formats.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str


class LabelError(Exception):
    pass


# GNSS types
SAT_SYS_GPS = 'G'
SAT_SYS_GLO = 'R'
SAT_SYS_GEO = 'S'  # Geostationary signal payload
SAT_SYS_GAL = 'E'  # Galileo
SAT_SYS_BDS = 'C'  # Compass/BeiDou
SAT_SYS_QZSS = 'J'
SAT_SYS_IRNSS = 'I'
SAT_SYS_MIX = 'M'  # Mixed files

# time systems
TIME_SYS_GPS = 'GPS'
TIME_SYS_GLO = 'GLO'


def codes(band, code):
    oc = str(band) + '{}'
    return tuple(oc.format(c) for c in code)


# observation types
# ps. range
C1 = ('C1',) + codes('C1', 'CSLXYMABCZ')
C2 = ('C2',) + codes('C2', 'CDSLXYMIQ')
C3 = ('C3I', 'C3Q', 'C3X')
C5 = ('C5',) + codes('C5', 'IQX')
C6 = ('C6',) + codes('C6', 'IQXABCZ')
C7 = ('C7',) + codes('C7', 'IQX')
C8 = ('C8',) + codes('C8', 'IQX')

P1 = ('P1', 'C1P', 'C1W')
P2 = ('P2', 'C2P', 'C2W')
P5 = ('P5',)
P6 = ('P6',)
P7 = ('P7',)
P8 = ('P8',)

# carr. phase
L1 = ('L1',) + codes('L1', 'CSLXPWYMNABCZ')
L2 = ('L2',) + codes('L2', 'CDSLXPWYMNIQ')
L3 = ('L3I', 'L3Q', 'L3X')
L5 = ('L5',) + codes('L5', 'IQX')
L6 = ('L6',) + codes('L6', 'IQXABCZ')
L7 = ('L7',) + codes('L7', 'IQX')
L8 = ('L8',) + codes('L8', 'IQX')

# doppler
D1 = ('D1',) + codes('D1', 'CSLXPWYMNABCZ')
D2 = ('D2',) + codes('D2', 'CDSLXPWYMNIQ')
D3 = ('D3I', 'D3Q', 'D3X')
D5 = ('D5',) + codes('D5', 'IQX')
D6 = ('D6',) + codes('D6', 'ABCXZ')
D7 = ('D7',) + codes('D7', 'IQX')
D8 = ('D8',) + codes('D8', 'IQX')

# signal strength
S1 = ('S1',) + codes('S1', 'CSLXPWYMNABCZ')
S2 = ('S2',) + codes('S2', 'CDSLXPWYMNIQ')
S3 = ('S3I', 'S3Q', 'S3X')
S5 = ('S5',) + codes('S5', 'IQX')
S6 = ('S6',) + codes('S6', 'IQXABCZ')
S7 = ('S7',) + codes('S7', 'IQX')
S8 = ('S8',) + codes('S8', 'IQX')

# loss-of-lock indicator for validity
LLI1 = ('LLI1',)
LLI2 = ('LLI2',)
LLI5 = ('LLI5',)

OBS_TYPE_LABELS = (
    C1, C2, C3, C5, C6, C7, C8,
    P1, P2, P5, P6, P7, P8,
    L1, L2, L3, L5, L6, L7, L8,
    S1, S2, S3, S5, S6, S7, S8,
    D1, D2, D3, D5, D6, D7, D8
)

LABELS = OBS_TYPE_LABELS + (LLI1, LLI2, LLI5)


def get_label(label):
    msg = 'No such label: {}.'.format(label)
    for type_set in LABELS:
        if label in type_set:
            return type_set

    # FIXME actual filename
    raise LabelError(msg)
