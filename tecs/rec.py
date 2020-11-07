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
from builtins import object

import tecs.label as label


class Rec(object):
    """ Base class for the output format record.

    Order corresponds to the output record; date/time value will be added later.
    """

    def __init__(self):
        self.formatDef = {
            label.R_TSN: {
                'format': '{0:11d}',
                'type': lambda v: int(v),
                'fortran': 'I11'
            },
            label.R_HOUR: {
                'format': '{1:14.11f}',
                'type': lambda v: float(v),
                'fortran': 'F14.11'
            },
            label.R_DATETIME: {
                'format': '{2}',
                'type': None,
                'fortran': None  # will set it later
            },
            label.R_ELEVATION: {
                'format': '{3: 10.5f}',
                'type': lambda v: float(v),
                'fortran': 'F10.5'
            },
            label.R_AZIMUTH: {
                'format': '{4: 11.5f}',
                'type': lambda v: float(v),
                'fortran': 'F11.5'
            },
            label.R_P1: {
                'format': '{5: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_P1_LLI: {
                'format': '{6:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_P2: {
                'format': '{7: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_P2_LLI: {
                'format': '{8:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_TEC_P1P2: {
                'format': '{9: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_L1: {
                'format': '{10: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_L1_LLI: {
                'format': '{11:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_L2: {
                'format': '{12: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_L2_LLI: {
                'format': '{13:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_TEC_L1L2: {
                'format': '{14: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_VALIDITY: {
                'format': '{15:7d}',
                'type': lambda v: int(v),
                'fortran': 'I7'
            },
            label.R_S1: {
                'format': '{16: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_S1_LLI: {
                'format': '{17:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_S2: {
                'format': '{18: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_S2_LLI: {
                'format': '{19:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_S5: {
                'format': '{20: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_S5_LLI: {
                'format': '{21:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_C1: {
                'format': '{22: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_C1_LLI: {
                'format': '{23:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_C2: {
                'format': '{24: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_C2_LLI: {
                'format': '{25:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_TEC_C1P2: {
                'format': '{26: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_TEC_L1C1: {
                'format': '{27: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_L5: {
                'format': '{28: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_L5_LLI: {
                'format': '{29:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_TEC_L1L5: {
                'format': '{30: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_C5: {
                'format': '{31: 16.3f}',
                'type': lambda v: float(v),
                'fortran': 'F16.3'
            },
            label.R_C5_LLI: {
                'format': '{32:1d}',
                'type': lambda v: int(v),
                'fortran': 'I1'
            },
            label.R_TEC_C1C5: {
                'format': '{33: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_TEC_L2L5: {
                'format': '{34: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_TEC_C1C2: {
                'format': '{35: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_TEC_C2C5: {
                'format': '{36: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_SAT_X: {
                'format': '{37: 23.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SAT_Y: {
                'format': '{38: 23.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SAT_Z: {
                'format': '{39: 23.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SITE_X: {
                'format': '{40: 23.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SITE_Y: {
                'format': '{41: 23.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SITE_Z: {
                'format': '{42: 23.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SITE_L: {
                'format': '{43: 17.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SITE_B: {
                'format': '{44: 16.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_SITE_H: {
                'format': '{45: 18.12f}',
                'type': lambda v: float(v),
                'fortran': 'F23.12'
            },
            label.R_TEC_L2L6: {
                'format': '{46: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_TEC_L2L7: {
                'format': '{47: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_TEC_L6L7: {
                'format': '{48: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_TEC_C2C6: {
                'format': '{49: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_TEC_C2C7: {
                'format': '{50: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_TEC_C6C7: {
                'format': '{51: 10.3f}',
                'type': lambda v: float(v),
                'fortran': 'F10.3'
            },
            label.R_TEC_L2C2: {
                'format': '{52: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
            label.R_TEC_L8C8: {
                'format': '{53: 21.3f}',
                'type': lambda v: float(v),
                'fortran': 'F21.3'
            },
        }
