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

"""
File: nmsg.py
Description: Navigation Message classes
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from builtins import object

from tecs.rinex.label import SAT_SYS_GPS, SAT_SYS_GLO, SAT_SYS_GAL, \
    SAT_SYS_GEO, SAT_SYS_BDS, SAT_SYS_QZSS, SAT_SYS_IRNSS

NAME = 'tecs.rinex.nmsg'


class GNSSNavigationMessage(object):
    system = None
    vals_per_orbit = ()

    date = None

    def __init__(self, number, epoch, sv_clock):
        self.number = number
        self.epoch = epoch
        self.sv_clock = sv_clock

        self.num_of_orbits = len(self.vals_per_orbit)

        self._message = None


class GPSNavigationMessage(GNSSNavigationMessage):
    system = SAT_SYS_GPS
    vals_per_orbit = (4, 4, 4, 4, 4, 4, 2)

    def __init__(self, number, epoch, sv_clock):
        super(GPSNavigationMessage, self).__init__(number, epoch, sv_clock)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value


class GLONASSNavigationMessage(GNSSNavigationMessage):
    system = SAT_SYS_GLO
    vals_per_orbit = (4, 4, 4)

    def __init__(self, number, epoch, sv_clock):
        super(GLONASSNavigationMessage, self).__init__(number, epoch, sv_clock)


class GalileoNavigationMessage(GPSNavigationMessage):
    system = SAT_SYS_GAL

    def __init__(self, number, epoch, sv_clock):
        super(GalileoNavigationMessage, self).__init__(number, epoch, sv_clock)


class SBASNavigationMessage(GLONASSNavigationMessage):
    system = SAT_SYS_GEO

    def __init__(self, number, epoch, sv_clock):
        super(SBASNavigationMessage, self).__init__(number, epoch, sv_clock)


class BDSNavigationMessage(GPSNavigationMessage):
    system = SAT_SYS_BDS

    def __init__(self, number, epoch, sv_clock):
        super(BDSNavigationMessage, self).__init__(number, epoch, sv_clock)


class QZSSNavigationMessage(GPSNavigationMessage):
    system = SAT_SYS_QZSS

    def __init__(self, number, epoch, sv_clock):
        super(QZSSNavigationMessage, self).__init__(number, epoch, sv_clock)


class QZSSSAIFNavigationMessage(GLONASSNavigationMessage):
    system = SAT_SYS_GEO  # FIXME is it right? move to SBAS?

    def __init__(self, number, epoch, sv_clock):
        super(QZSSSAIFNavigationMessage, self).__init__(number, epoch, sv_clock)


class IRNSSNavigationMessage(GPSNavigationMessage):
    system = SAT_SYS_IRNSS

    def __init__(self, number, epoch, sv_clock):
        super(IRNSSNavigationMessage, self).__init__(number, epoch, sv_clock)
