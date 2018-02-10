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
File: n.py
Description: GNSS navigation message file ver2.n
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import map

import logging

from tecs.rinex.basic import NavigationMessage, read_header, RinexError
from tecs.rinex.common import validate_epoch, sec2sec_ms
from tecs.rinex.header import RinexVersionType
from tecs.rinex.nmsg import GPSNavigationMessage, GLONASSNavigationMessage, \
    SBASNavigationMessage

NAME = 'tecs.rinex.v2.n'


class Nav2(NavigationMessage):
    _name = NAME + '.Nav2'

    version = 2.0

    rec_len = 19
    orbit_start = 3
    orbit_end = 75

    spaces = 3  # amount of spaces at the start of the orbit record line

    systems = (GPSNavigationMessage, GLONASSNavigationMessage)
    file_types = {
        'N': GPSNavigationMessage.system,
        'G': GLONASSNavigationMessage.system,
    }

    def __init__(self, f_obj, filename):
        super(Nav2, self).__init__(f_obj, filename)

        self.msg_reader = {}
        for s in self.systems:
            self.msg_reader[s.system] = s

        self.ver_type = RinexVersionType(self.version)
        self.date = self.filename_date

        header = read_header(f_obj)
        self._parse_header(header)

        self.message = {}
        try:
            self._read_message()
        finally:
            self._fobj.close()

    def _read_message(self):

        logger = logging.getLogger(self._name + '._read_message')

        orbits = []
        num_of_orbits = 0
        system, num, epoch, sv_clock, reader = (None,) * 5
        vals_per_orbit = None

        for line in self._fobj:
            # sv/epoch/sc clock
            if not line[0:self.spaces].isspace():
                system, num, epoch, sv_clock = self._parse_epoch_record(
                    line)

                if system in self.msg_reader:
                    reader = self.msg_reader[system](num, epoch, sv_clock)
                else:
                    msg = "unknown satellite system '{}'.".format(system)
                    raise RinexError(self.filename, msg)

                vals_per_orbit = reader.vals_per_orbit
                num_of_orbits = reader.num_of_orbits
                continue

            # broadcast orbits
            if num_of_orbits:
                orbits.append(line)
                num_of_orbits -= 1
                if num_of_orbits:
                    continue

            if reader is None or vals_per_orbit is None:
                msg = 'error occurred while reading the file.'
                raise RinexError(self.filename, msg)

            if self.date != epoch.date():
                msg_fmt = ("date extracted from the file name '{}' doesn't "
                           "match the date of the navigation message: "
                           "{} != {} ({}).")
                msg = msg_fmt.format(self.filename,
                                     self.date,
                                     epoch.date(),
                                     epoch.time())
                logger.info(msg)

                orbits = []
                reader = None
                continue

            # message
            reader.message = self._read_orbits(orbits, vals_per_orbit)

            if system not in self.message:
                self.message[system] = {}
            if num not in self.message[system]:
                self.message[system][num] = {}

            self.message[system][num][epoch.time()] = tuple(reader.message)

            orbits = []
            reader = None

    def _read_orbits(self, orbits, vals_per_orbit):
        broadcast_orbits = []

        # for line in orbits:
        for orbit_num in range(len(orbits)):
            line = orbits[orbit_num].rstrip()

            values = [
                line[i:i + self.rec_len].rstrip().lower().replace('d', 'e')

                for i in range(
                    self.orbit_start,
                    self.orbit_end,
                    self.rec_len)
                ]

            try:
                values = values[:vals_per_orbit[orbit_num]]
                values = [s and float(s) or 0. for s in values]
            except (ValueError, IndexError):
                msg = "can't read the message: {}".format(line)
                raise RinexError(self.filename, msg)

            broadcast_orbits += values

        return broadcast_orbits

    def _parse_epoch_record(self, epoch_record):
        system = self.ver_type.value[1]
        number = epoch_record[0:2]

        # year, month, day, hour, min; +sec
        epoch = [epoch_record[i:i + 3] for i in range(2, 17, 3)]
        sec = epoch_record[17:22]

        sv_clock = [epoch_record[i:i + 19] for i in (22, 41, 60)]
        sv_clock = [i.lower().replace('d', 'e') for i in sv_clock]

        try:
            system = self.file_types[system]
            number = int(number)
            sec = sec2sec_ms(float(sec))
            epoch = list(map(int, epoch))
            epoch += list(sec)
            epoch = validate_epoch(epoch)
            sv_clock = list(map(float, sv_clock))
        except (ValueError, KeyError):
            msg = "Can't read epoch: {}.".format(epoch_record)
            raise RinexError(self.filename, msg)

        return system, number, epoch, tuple(sv_clock)

    def _next_rec(self, f_obj):
        pass


class Nav21(Nav2):
    _name = NAME + '.Nav21'
    version = 2.1
    systems = Nav2.systems + (SBASNavigationMessage,)
    file_types = {
        'N': GPSNavigationMessage.system,
        'G': GLONASSNavigationMessage.system,
        'H': SBASNavigationMessage.system
    }

    def __init__(self, f_obj, filename):
        super(Nav21, self).__init__(f_obj, filename)


class Nav211(Nav21):
    _name = NAME + '.Nav211'
    version = 2.11

    def __init__(self, f_obj, filename):
        super(Nav211, self).__init__(f_obj, filename)
