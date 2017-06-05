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

"""
File: n.py
Description: GNSS RINEX observation data reader ver2.n
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import math
import re

from tecs.rinex.basic import ObservationData
from tecs.rinex.basic import RinexError
from tecs.rinex.common import validate_epoch
from tecs.rinex.header import RinexVersionType, ApproxPositionXYX, Interval, \
    TimeOfFirstObs

NAME = 'tecs.rinex.v2.o'
LOGGER = logging.getLogger(NAME)


class Obs2(ObservationData):
    """Obs2(f_obj, filename, settings=None) -> instance

    GPS observation data file ver.2.0

    Parameters
    ----------
    f_obj : file
        file-like object

    filename : str
        a name of the file; we should use it because f_obj.name contains not
        filename.
    """

    VERSION = 2.0
    REC_LEN = 16

    OBS_TYPES = re.compile(r'\s{4}([LCPDT][12])')

    RE_TOBS = re.compile(r'(.*)# / TYPES OF OBSERV')
    RE_END_HEADER = re.compile(r'(.*)END OF HEADER')
    RE_COMMENT = re.compile(r'(.*)COMMENT')

    END_OF_HEADER = 'END OF HEADER'

    def _get_val(self, rec, i, rlen):
        """get_val(rec, i, rlen) -> val, lli, sig_strength

        parse the record rec to retrieve observation values: val, LLI
        and signal strength.

        Parameters
        ----------
        rec : str
            the whole record to parse
        i : int
            start of an observation data substring
        rlen : int
            length of the substring
        """

        val = rec[i:i + rlen]

        digs = '0123456789'
        spaces = ' ' * len(val)

        if val and val != spaces:
            # observation
            try:
                obs = val[:14]
                obs = float(obs)
            except ValueError:
                err = "wrong data string:\n%s" % rec
                raise RinexError(self.filename, err)
            val = val[14:]

            # LLI
            try:
                lli = val[0]
                if lli in digs:
                    lli = int(lli)
                else:
                    lli = 0
            except IndexError:
                lli = 0

            # Signal strength
            try:
                sig_strength = val[1]
                if sig_strength in digs:
                    sig_strength = int(sig_strength)
                else:
                    sig_strength = 0
            except IndexError:
                sig_strength = 0

        else:
            obs = None
            lli = 0
            sig_strength = 0

        return obs, lli, sig_strength

    def _get_prn(self, rec, i, cur_epoch):
        """get_prn(rec, i) -> prn"""
        val = rec[i:i + 3]
        if not val:
            err = "can't extract satellite:\n%s <%s>" % (cur_epoch, rec)
            raise RinexError(self.filename, err)

        # system identifier
        cur_sys = val[0].upper()
        if cur_sys == ' ':
            cur_sys = 'G'

        # satellite number
        cur_sat = None
        try:
            cur_sat = val[1:]
            cur_sat = int(cur_sat)
        except ValueError:
            err = 'wrong PRN (%s) in epoch record:\n<%s>' % (
                cur_sat, cur_epoch)
            raise RinexError(self.filename, err)

        cur_sat = "%02d" % cur_sat

        # PRN
        cur_prn = cur_sys + cur_sat
        return cur_prn

    def get_interval(self, n):
        """get_interval(n) -> interval

        Get an observation interval using first n epochs of an observation file.

        Parameters
        ----------
        n : int
            amount of epochs to read

        Returns
        -------
        interval : float
            observation interval, seconds
        """

        epoch = None
        epoch_count = 0
        deltas = []
        dt = None

        records = self.read_records()

        try:
            while epoch_count < n:
                rec = next(records)

                if not epoch:
                    epoch = rec[0]
                    continue

                elif epoch == rec[0]:
                    continue

                dt = rec[0] - epoch

                if dt:
                    deltas.append(dt.total_seconds())
                    epoch_count += 1

                epoch = rec[0]

        except RinexError as err:
            msg = ("Can't find out obs interval: %s" % str(err))
            raise RinexError(self.filename, msg)

        except StopIteration as err:
            if dt is None:
                msg = ("Can't find out obs interval: %s" % str(err))
                raise RinexError(self.filename, msg)
            else:
                pass

        records.close()
        del records

        if len(set(deltas)) == 1:
            interval = deltas[0]

        else:
            dt_dict = {}

            for dt in deltas:
                if dt not in dt_dict:
                    dt_dict[dt] = 1
                else:
                    dt_dict[dt] += 1

            tmp = list(dt_dict.keys())
            tmp.sort(key=lambda k: dt_dict[k], reverse=True)

            interval = tmp[0]

        self._fobj.seek(0)
        for rec in self._fobj:
            rec = rec[60:].rstrip()
            if rec == self.END_OF_HEADER:
                break

        return interval

    def set_obs_num_types(self, header):
        """set_obs_num_types(header) -> None

        Parameters
        ----------
        header : list

        check and set value of the self.properties['obs types']
        """
        obs_types = []

        def get_o_types(r, n, l):
            """get_o_types(r, n, l) -> obs_types

            Parameters
            ----------
            r : str
                substring
            n : int
                amount of observations
            l : int
                len of the record

            Returns
            -------
            obs_types : list
                list of the observation types
            """
            o_types = []

            for i in range(0, n * l, l):
                cur_o_type = r[i:i + l]
                match = re.match(self.OBS_TYPES, cur_o_type)

                if not match:
                    msg = "Unknown observation type: '%s'\n%s" % (
                        cur_o_type, r.rstrip())
                    self._logger.warning(msg)

                cur_o_type = cur_o_type[-2:]
                o_types.append(cur_o_type)

            return o_types

        for (idx, rec) in enumerate(header):

            if not self.RE_TOBS.match(rec):
                continue

            try:
                obs_num = rec[:6]
                obs_num = int(obs_num)
            except (IndexError, ValueError):
                err = ('Can\'t read the number of the observation types:\n'
                       '                <%s>') % rec.rstrip()
                raise RinexError(self.filename, err)

            if obs_num > 9:
                obs_types = []

                num_compl_lines = obs_num // 9

                for cur_l in range(num_compl_lines):
                    obs_types_line = header[idx + cur_l]
                    obs_types += get_o_types(obs_types_line[6:60], 9, 6)

                if obs_num % 9:
                    rest_num = obs_num - num_compl_lines * 9
                    obs_types_line = header[idx + num_compl_lines]
                    obs_types += get_o_types(obs_types_line[6:6 + rest_num * 6],
                                             rest_num,
                                             6)
            else:
                obs_types = get_o_types(rec[6:6 + obs_num * 6], obs_num, 6)

            if obs_num != len(obs_types):
                err = """Can't extract some observation types from:
                '%s'""" % rec.rstrip()
                raise RinexError(self.filename, err)

            break

        self.properties['obs types'] = tuple(obs_types)

    def set_logger(self):
        """ set_logger()
        """
        self._logger = logging.getLogger(NAME + '.Obs2')

    def read_epoch(self, epoch):
        """
        read_epoch(epoch) -> epoch_components

        parse epoch record.

        Parameters
        ----------
        epoch : str
            epoch record

        Returns
        -------
        epoch_components : tuple
            (datetime, epoch-flag, num-of-satellites, rcvr-clock-offset, prns)
        """

        # assume that the first element is an epoch

        # 1. epoch flag
        try:
            epoch_flag = int(epoch[26:29])
        except ValueError:
            err = 'wrong epoch flag in epoch record\n%s' % epoch
            raise RinexError(self.filename, err)

        # set sat_num & return, need no date
        if epoch_flag > 1:

            msg = "epoch flag >1 (%s: %s)" % (self.filename, epoch)
            self._logger.info(msg)

            try:
                sat_num = int(epoch[29:32])
                return None, epoch_flag, sat_num, None, None

            except ValueError:
                err = "wrong event flag:\n%s" % epoch
                raise RinexError(self.filename, err)

        # 2. date
        try:
            d = []
            for i in range(0, 13, 3):
                val = epoch[i:i + 3]
                val = int(val)
                d.append(val)

            sec = float(epoch[15:26])
            microsec = (sec - int(sec)) * 1e+6
            microsec = float("%.5f" % microsec)

            d.append(int(sec))
            d.append(int(microsec))

            cur_epoch = validate_epoch(d)

        except (IndexError, ValueError) as err:
            msg = "wrong date in epoch record '%s': %s" % (epoch, str(err))
            raise RinexError(self.filename, msg)

        try:
            receiver_offset = epoch[68:]
            receiver_offset = float(receiver_offset)
        except (IndexError, ValueError):
            receiver_offset = 0.0

        # 3. num of satellites
        try:
            sat_num = epoch[29:32]
            sat_num = int(sat_num)
        except ValueError:
            err = 'wrong satellite number in epoch record:\n%s' % epoch
            raise RinexError(self.filename, err)

        # 4. list of PRNs (sat.num + sys identifier)
        prev_epoch_line = ''
        prns = []

        # > 12
        if sat_num > 12:
            num_compl_lines = sat_num // 12
            rest_sat_num = sat_num - num_compl_lines * 12

            # read strings which contain 12 satellites
            # - current row
            for i in range(32, 66, 3):
                cur_prn = self._get_prn(epoch, i, cur_epoch)
                prns.append(cur_prn)
            num_compl_lines -= 1

            # - next rows (12 sat per row)
            while num_compl_lines:
                num_compl_lines -= 1
                epoch = self._next_rec(self._fobj)

                for i in range(32, 66, 3):
                    cur_prn = self._get_prn(epoch, i, cur_epoch)
                    prns.append(cur_prn)

            # - the last one (if any)
            if rest_sat_num:
                epoch = self._next_rec(self._fobj)

                r_stop = 32 + rest_sat_num * 3 - 2
                for i in range(32, r_stop, 3):
                    cur_prn = self._get_prn(epoch, i, cur_epoch)
                    prns.append(cur_prn)

        # < 12
        else:
            for i in range(32, 32 + 3 * sat_num - 2, 3):
                cur_prn = self._get_prn(epoch, i, cur_epoch)
                prns.append(cur_prn)

        if sat_num != len(prns):
            err = "can't extract all PRNs from epoch line:\n%s\n%s" % (
                prev_epoch_line, epoch)
            raise RinexError(self.filename, err)

        return cur_epoch, epoch_flag, sat_num, receiver_offset, prns

    def read_records(self):
        """read_records() -> generator

        Returns
        -------
            dataset : tuple
            (epoch, sat, data) with
                data = { obs_1: val, obs_2: val, ... }
        """

        for line in self._fobj:
            (cur_epoch, epoch_flag,
             sat_num, receiver_offset, prns) = self.read_epoch(line.rstrip())

            # if the flag != 0

            # 1. Power failure between previous and current epoch
            if epoch_flag == 1:
                msg = ('%s - power failure between previous and current '
                       'epoch %s.') % (self.filename, cur_epoch)
                self._logger.info(msg)

            # 3. New site occupation
            elif epoch_flag == 3:
                msg = "New site occupation: {} - {}."
                msg = msg.format(cur_epoch, self.filename)
                self._logger.info(msg)

                header_slice = []
                while sat_num > 0:
                    h_str = self._next_rec(self._fobj)
                    header_slice.append(h_str)
                    sat_num -= 1

                self._parse_header(header_slice)
                continue

            # 4. Header information
            elif epoch_flag == 4:
                header_slice = []
                while sat_num > 0:
                    sat_num -= 1
                    h_str = self._next_rec(self._fobj)
                    header_slice.append(h_str)
                    msg = "%s: %s." % (self.filename, h_str)
                    self._logger.debug(msg)

                self._parse_header(header_slice)
                continue

            # n. Some other
            elif epoch_flag > 1:
                msg = 'epoch flag = %s; %s record(s) to follow: %s - %s.' % (
                    epoch_flag, sat_num, cur_epoch, self.filename)
                self._logger.debug(msg)

                while sat_num > 0:
                    msg = self._next_rec(self._fobj)

                    self._logger.debug(msg)
                    sat_num -= 1

                continue

            # FIXME should I?
            if receiver_offset:
                pass

            # read the records
            for cur_prn in prns:

                data = []

                for n in self.lines_per_rec:
                    rec = self._next_rec(self._fobj)

                    rend = n * self.REC_LEN - (self.REC_LEN - 1)
                    rstep = self.REC_LEN

                    for i in range(0, rend, rstep):
                        (val, lli, sig_strength) = (
                            self._get_val(rec, i, self.REC_LEN))

                        data.append((val, lli, sig_strength))

                types_n_vals = {}

                for i in range(len(data)):
                    o_type = self.properties['obs types'][i]
                    val = data[i]
                    types_n_vals[o_type] = val

                # it could be epoch duplicate: just skip
                if cur_epoch == self.preceding_epoch:
                    msg = "%s - duplicate dates: %s" % (
                        self.filename, str(cur_epoch))
                    self._logger.info(msg)
                    continue

                yield (cur_epoch, cur_prn, types_n_vals)

            self.preceding_epoch = cur_epoch

    def __init__(self, f_obj, filename):
        """ """
        super(Obs2, self).__init__(f_obj, filename)

        self._logger = None
        self.set_logger()

        # previous epoch to find duplicates
        self.preceding_epoch = None

        self.properties = {
            'obs types': (None,),
        }

        self.lines_per_rec = []

        file_header = []
        for rec in self._fobj:
            if self.RE_END_HEADER.match(rec):
                break
            file_header.append(rec)

        self.set_obs_num_types(file_header)
        self._det_lines_per_rec()

        # header labels
        self.ver_type = RinexVersionType(self.VERSION)
        self.tofo = TimeOfFirstObs(self.VERSION)
        self.xyz = ApproxPositionXYX(self.VERSION)
        self.interval = Interval(self.VERSION)

        self._parse_header(file_header)

        dt = self.get_interval(10)

        if self.interval.value != dt:
            msg_wi = 'Wrong interval value in the header of {}: {}; ' \
                     'using {} instead.'
            self._logger.warning(msg_wi.format(self.filename,
                                               self.interval.value,
                                               dt))

        self.interval.value = '{:10.3f}'.format(dt)

    def _det_lines_per_rec(self):
        """_det_lines_per_rec()

        determine amount of the lines per record.
        """

        obs_num = len(self.properties['obs types'])
        s2flw = obs_num / 5.
        s2flw = math.ceil(s2flw)
        s2flw = int(s2flw)

        lines_per_rec = []

        n = obs_num
        for s in range(s2flw):
            n -= 5
            if n < 0:
                lines_per_rec.append(n + 5)
            elif n >= 0:
                lines_per_rec.append(5)

        self.lines_per_rec = lines_per_rec

        del lines_per_rec
        del obs_num

    def __del__(self):
        self._fobj.close()


class Obs21(Obs2):
    """RINEX obs v2.11"""
    VERSION = 2.1

    # (F14.3,I1,I1)
    REC_LEN = 16

    OBS_TYPES = re.compile(r'\s{4}([LCPDTS][12])')

    def set_logger(self):
        self._logger = logging.getLogger(NAME + '.Obs21')


class Obs211(Obs21):
    """RINEX obs v2.11"""
    VERSION = 2.11

    # (F14.3,I1,I1)
    REC_LEN = 16

    OBS_TYPES = re.compile(r'\s{4}([LCPDS][125678])')

    def set_logger(self):
        self._logger = logging.getLogger(NAME + '.Obs211')
