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
File: header.py
Description: collection of header records classes.
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from builtins import map
from builtins import str
from builtins import range
from builtins import object

from tecs.rinex.common import sec2sec_ms, validate_epoch
from tecs.rinex.label import SAT_SYS_BDS

NAME = 'tecs.rinex.header'


class HeaderError(Exception):
    pass


class HeaderLabel(object):
    def __init__(self, version):
        """"""
        self.version = version
        self.label = None
        self.str_msg = '{label}: {value}'

        self._value = None

    def __bool__(self):
        if self._value:
            return True
        else:
            return False

    def __str__(self):
        return self.str_msg.format(label=self.label, value=str(self._value))


class EndOfHeader(HeaderLabel):
    def __init__(self, version):
        super(EndOfHeader, self).__init__(version)
        self.label = 'END OF HEADER'


class RinexVersionType(HeaderLabel):
    def __init__(self, version):
        super(RinexVersionType, self).__init__(version)
        self.label = 'RINEX VERSION / TYPE'

    @property
    def value(self):
        # type: () -> tuple
        return self._value

    @value.setter
    def value(self, header_slice):
        rinex_version = float(header_slice[:9])
        file_type = header_slice[20]
        satellite_system = header_slice[40]

        if self.version < 3:
            if satellite_system == ' ':
                satellite_system = 'G'

        self._value = (rinex_version, file_type, satellite_system)


class TimeOfFirstObs(HeaderLabel):
    """TimeOfFirstObs

    Attributes
    ----------
    self.value : tuple
        value = (epoch, time_system)
    """

    def __init__(self, version):
        super(TimeOfFirstObs, self).__init__(version)
        self.label = 'TIME OF FIRST OBS'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, header_slice):
        epoch = [header_slice[i:i + 6] for i in range(0, 30, 6)]
        epoch = list(map(int, epoch))

        if self.version == 2.0:
            sec = float(header_slice[30:43])
        else:
            sec = float(header_slice[30:44])

        sec, microsec = sec2sec_ms(sec)

        epoch += [sec, microsec]
        epoch = validate_epoch(epoch)

        time_system = header_slice[48:51]

        if time_system == '   ':
            if self.version >= 3:
                # what should I do?
                pass
            time_system = 'GPS'

        self._value = (epoch, time_system)


class ApproxPositionXYX(HeaderLabel):
    """ApproxPositionXYX

    Attributes
    ----------
    self.value : tuple
        value = (x, y, z)
    """

    def __init__(self, version):
        super(ApproxPositionXYX, self).__init__(version)
        self.label = 'APPROX POSITION XYZ'
        self._value = (0., 0., 0.)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, header_slice):
        xyz = [header_slice[i:i + 14] for i in range(0, 42, 14)]
        xyz = list(map(float, xyz))

        self._value = tuple(xyz)


class Interval(HeaderLabel):
    """Interval

    Attributes
    ----------
    self.value : float
        value = interval
    """
    def __init__(self, version):
        super(Interval, self).__init__(version)
        self.label = 'INTERVAL'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, header_slice):
        if self.version == 2.0:
            self._value = int(header_slice[:6])
        else:
            self._value = float(header_slice[:10])


class SysNObsTypes(HeaderLabel):
    """SysNObsTypes

    Attributes
    ----------
    self.value : dict
        value = {sat_sys: (obs_types,)}
    """
    def __init__(self, version):
        super(SysNObsTypes, self).__init__(version)
        self.label = 'SYS / # / OBS TYPES'
        self._value = {}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, header_slice):
        sys_n_obs = []
        wn_msg = 'Wrong number of observations {ot} (expected {n}).'

        for line in header_slice.split('\n'):
            if not line:
                continue
            elif line[0:6].isspace():
                sys_n_obs[-1] += line[7:60]
            else:
                sys_n_obs.append(line[:60])

        for sno in sys_n_obs:
            obs = sno.split()

            sat_sys = obs[0]
            num_of_obs = int(obs[1])
            obs_types = tuple(obs[2:])

            # misunderstanding with band #1 in Compass/BeiDou
            if self.version >= 3.02 and sat_sys == SAT_SYS_BDS:
                corrected_obs_types = list(obs_types)
                for i, t in enumerate(corrected_obs_types):
                    if t[1] == '1':
                        t = t.replace('1', '2')
                        corrected_obs_types[i] = t
                obs_types = tuple(corrected_obs_types)

            assert len(obs_types) == num_of_obs, wn_msg.format(
                ot=len(obs_types), n=num_of_obs
            )

            if sat_sys in self._value:
                msg = "Got a duplicate of the satellite system" \
                      " in OBS_TYPES: '{ss}'".format(ss=sat_sys)
                raise HeaderError(msg)

            self._value[sat_sys] = obs_types
