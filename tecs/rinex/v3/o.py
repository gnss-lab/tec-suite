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
File: v3.py
Description: RINEX v 3.n
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from builtins import map

import logging
from datetime import timedelta

from tecs.rinex.basic import ObservationData
from tecs.rinex.basic import RinexError
from tecs.rinex.common import validate_epoch, sec2sec_ms
from tecs.rinex.header import RinexVersionType, TimeOfFirstObs, \
    ApproxPositionXYX, Interval, SysNObsTypes

NAME = 'tecs.rinex.o.v3'


class Obs3(ObservationData):
    """RINEX v3.00 observation data
    """
    VERSION = 3.0

    _epoch_id = '>'
    _obs_rec_len = 16

    def __init__(self, fobj, filename):
        super(Obs3, self).__init__(fobj, filename)

        self._name = NAME + '.Obs3'

        # header labels
        self.ver_type = RinexVersionType(self.VERSION)
        self.tofo = TimeOfFirstObs(self.VERSION)
        self.xyz = ApproxPositionXYX(self.VERSION)
        self.interval = Interval(self.VERSION)
        self.sys_n_obs = SysNObsTypes(self.VERSION)

        header = []
        for line in self._fobj:
            label = line[60:].rstrip()
            if label == 'END OF HEADER':
                break
            header.append(line)

        self._parse_header(header)

        self._det_interval()

        self._data_chunks = []
        self._det_data_chunks()

    def _next_rec(self, f_obj):
        pass

    def _det_data_chunks(self):
        """_det_data_chunks(self) -> None

        determinate data chunks list.
        """
        ns_obs = [len(self.sys_n_obs.value[d]) for d in self.sys_n_obs.value]
        max_n_obs = max(ns_obs)

        rl = self._obs_rec_len

        start = 3
        stop = max_n_obs * rl + rl
        steps = range(start, stop, rl)

        chunks = []
        for i in range(len(steps) - 1):
            chunks.append((steps[i], steps[i + 1]))

        self._data_chunks = tuple(chunks)

    def _det_interval(self):
        err_msg = 'invalid interval value: {}'
        logger = logging.getLogger(self._name + '._det_interval')

        epoch_records = [
            self._next_epoch(),
            self._next_epoch()
        ]

        while epoch_records[0] == epoch_records[1]:
            epoch_records[1] = self._next_epoch()

        for er in epoch_records:
            if er is None:
                raise RinexError(self.filename, err_msg.format('None'))

        dt = epoch_records[1] - epoch_records[0]
        dt = dt.total_seconds()

        if dt <= 0:
            raise RinexError(self.filename, err_msg.format(dt))

        if self.interval.value != dt:
            msg_wi = 'Wrong interval value in the header of {}: {}; ' \
                     'using {} instead.'
            logger.warning(msg_wi.format(self.filename,
                                         self.interval.value,
                                         dt))

        self.interval.value = '{:10.3f}'.format(dt)

        self._fobj.seek(0)
        for line in self._fobj:
            line = line[60:].rstrip()
            if line == 'END OF HEADER':
                break

    def _next_epoch(self):
        """_next_epoch() -> None

        retrieves datetime of the next epoch record.

        Notes
        -----
        changes self._fobj position.
        """
        epoch = None
        for line in self._fobj:
            if not line[0] == self._epoch_id:
                continue
            epoch, flag = self._parse_epoch_record(line)[0:2]
            # special event: no epoch
            if flag > 1:
                continue
            break
        return epoch

    # noinspection PyProtectedMember
    def _parse_header(self, header):
        super(Obs3, self)._parse_header(header)

        sys_n_obs_slice = ''
        for line in header:
            label = line[60:].rstrip()
            if self.sys_n_obs.label == label:
                sys_n_obs_slice += line
                continue

        self.sys_n_obs.value = sys_n_obs_slice

    def _parse_epoch_record(self, epoch_record):
        """parse_epoch_record(epoch_record)

        Parameters
        ----------
        epoch_record : str

        Returns
        -------
        epoch_components : tuple
            (epoch, epoch_flag, num_of_sat, clock_offset)

            with
            epoch: datetime,
            epoch_flag: int,
            num_of_sat: int
            clock_offset: datetime.timedelta

        Notes
        -----
        timestamps accurate to microsecond
        """

        if not epoch_record[0] == self._epoch_id:
            msg = 'not epoch record: {rec}'.format(rec=epoch_record)
            raise RinexError(self.filename, msg)

        # month, day, hour, min; year + ...
        epoch = [epoch_record[i:i + 3] for i in range(6, 17, 3)]
        epoch = [epoch_record[1:6]] + epoch

        sec = epoch_record[18:29]

        try:
            sec = float(sec)
            sec, micro_sec = sec2sec_ms(sec)

            epoch += [sec, micro_sec]
            epoch = list(map(int, epoch))

            epoch = validate_epoch(epoch)
        except ValueError:
            epoch = None

        try:
            epoch_flag = int(epoch_record[31])
        except (IndexError, ValueError):
            msg = "Can't extract epoch flag from {rec}".format(rec=epoch_record)
            raise RinexError(self.filename, msg)

        try:
            num_of_sat = int(epoch_record[32:35])
        except ValueError:
            msg = "Can't extract" \
                  " number of satellites from {rec}".format(rec=epoch_record)
            raise RinexError(self.filename, msg)

        try:
            sec = float(epoch_record[42:])
            sec, micro_sec = sec2sec_ms(sec)
            clock_offset = timedelta(0, sec, micro_sec)
        except ValueError:
            clock_offset = timedelta(0)

        return epoch, epoch_flag, num_of_sat, clock_offset

    def _parse_obs_record(self, record):
        """parse_obs_record(record) -> sat, obs_values

        Parameters
        ----------
        record : str

        Returns
        -------
        sat : str
            satellite
        obs_values : tuple
            (obs_values_1, ..., obs_values_n)
            with obs_values_x = (obs_value, lli_value, sig_strength_value)
        """

        sat = record[0:3]
        if not sat:
            msg = "Can't extract satellite from {rec}".format(rec=record)
            raise RinexError(self.filename, msg)

        sat = sat.replace(' ', '0')

        if sat[0] not in self.sys_n_obs.value:
            msg = 'There is no such satellite system definition in header:' \
                  ' {ss}.'.format(ss=sat[0])
            raise RinexError(self.filename, msg)

        data_record = []
        empty = (0,) * 3

        obs_num = len(self.sys_n_obs.value[sat[0]])

        for n in range(obs_num):
            s, e = self._data_chunks[n]
            chunk = record[s:e]

            if not chunk or chunk.isspace():
                data_record.append(empty)
                continue

            val = chunk[:14]
            try:
                if not val or val.isspace():
                    val = 0.0
                else:
                    val = float(val)
            except ValueError:
                val = 0.0

            feature = []
            for i in 14, 15:
                try:
                    v = chunk[i]
                    if v.isspace():
                        v = 0
                    else:
                        v = int(v)
                except (IndexError, ValueError):
                    v = 0
                feature.append(v)

            data_record.append((val, feature[0], feature[1]))

        return sat, tuple(data_record)

    # noinspection PyUnusedLocal
    def _handle_event(self, epoch, epoch_flag, special_records):
        logger = logging.getLogger(self._name + '._handle_event')

        # header information follows
        if epoch_flag == 4:
            self._parse_header(special_records)
        # TODO add another event types handlers
        # in that case 'epoch' param may be useful here
        else:
            msg = 'Missed event type: {flag}'.format(flag=epoch_flag)
            logger.error(msg)

    def _handle_power_failure(self, epoch):
        logger = logging.getLogger(self._name + '_handle_power_failure')
        msg = '{file} {epoch}: ' \
              'power failure between previous and current epoch.'
        msg = msg.format(file=self.filename, epoch=epoch)
        logger.info(msg)

    def read_records(self):
        """read_records() -> generator

        iterate over data records it the file; return (epoch, sat, dataset).
        """
        epoch, epoch_flag, num_of_sat, clock_offset = (None,) * 4
        special_records = []

        for line in self._fobj:
            if line[0] == self._epoch_id:
                epoch, epoch_flag, num_of_sat, clock_offset = \
                    self._parse_epoch_record(line)
                continue

            if epoch_flag > 1:
                if num_of_sat > 0:
                    special_records.append(line)
                    num_of_sat -= 1

                if num_of_sat == 0:
                    self._handle_event(epoch, epoch_flag, special_records)

                continue

            if epoch_flag == 1:
                self._handle_power_failure(epoch)
                epoch_flag = 0

            if num_of_sat > 0:
                num_of_sat -= 1
                sat, dataset = self._parse_obs_record(line)

                if not sat[0] in self.sys_n_obs.value:
                    msg = 'No such satellite {}'.format(sat)
                    raise RinexError(self.filename, msg)

                # imitation of o.v2.Obs return
                sat_obs = self.sys_n_obs.value[sat[0]]
                assert len(dataset) == len(sat_obs)

                rec = {}
                for i, val in enumerate(dataset):
                    rec[sat_obs[i]] = val

                yield epoch, sat, rec


class Obs301(Obs3):
    """Obs301
    """
    VERSION = 3.01

    def __init__(self, fobj, filename):
        super(Obs301, self).__init__(fobj, filename)


class Obs302(Obs301):
    """Obs302
    """
    VERSION = 3.02

    def __init__(self, fobj, filename):
        super(Obs302, self).__init__(fobj, filename)


class Obs303(Obs302):
    """Obs303
    """
    VERSION = 3.03

    def __init__(self, fobj, filename):
        super(Obs303, self).__init__(fobj, filename)
