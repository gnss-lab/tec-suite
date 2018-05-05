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
File: p.py
Description: mixed GNSS navigation message file
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import map

from tecs.rinex.basic import RinexError
from tecs.rinex.common import validate_epoch
from tecs.rinex.nmsg import GPSNavigationMessage, GLONASSNavigationMessage, \
    GalileoNavigationMessage, SBASNavigationMessage, BDSNavigationMessage, \
    QZSSNavigationMessage, IRNSSNavigationMessage
from tecs.rinex.v2.n import Nav2

NAME = 'tecs.rinex.v3.n'


class Nav3(Nav2):
    _name = NAME + '.Nav3'

    version = 3.0

    orbit_start = 4
    orbit_end = 76

    spaces = 1

    systems = (
        GPSNavigationMessage,
        GLONASSNavigationMessage,
        GalileoNavigationMessage,
        SBASNavigationMessage,
        BDSNavigationMessage,
        QZSSNavigationMessage,
        IRNSSNavigationMessage,
    )
    
    file_types = None

    def _parse_epoch_record(self, epoch_record):
        """_parse_epoch_record(self, epoch_record) -> epoch_components

        Parameters
        ----------
        epoch_record : str

        Returns
        -------
        epoch_components : tuple
            (satellite_system, satellite_number, epoch, sv_clock)
        """
        system = epoch_record[0]
        number = epoch_record[1:3]

        # month, day, hour, min, sec; year + ...
        epoch = [epoch_record[i:i + 3] for i in range(8, 23, 3)]
        epoch = [epoch_record[4:9]] + epoch

        sv_clock = [epoch_record[i:i + 19] for i in (23, 42, 61)]
        sv_clock = [i.lower().replace('d', 'e') for i in sv_clock]

        try:
            number = int(number)
            epoch = list(map(int, epoch))
            epoch = validate_epoch(epoch)
            sv_clock = list(map(float, sv_clock))
        except ValueError:
            msg = "Can't read epoch: {}.".format(epoch_record)
            raise RinexError(self.filename, msg)

        return system, number, epoch, tuple(sv_clock)


class Nav301(Nav3):
    _name = NAME + '.Nav301'
    version = 3.01
    systems = Nav3.systems


class Nav302(Nav301):
    _name = NAME + '.Nav302'
    version = 3.02


class Nav303(Nav302):
    _name = NAME + '.Nav303'
    version = 3.03
