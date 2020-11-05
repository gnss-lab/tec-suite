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

"""Text files writer.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from builtins import object

import datetime
import logging
import math
import os
import os.path
import re

import tecs.label
from tecs import dio

EXT = dio.OUT_EXT[tecs.label.OUT_FILE_TEXT]
NAME = 'tecs.dio.text'


class TextError(Exception):
    """TextError(Exception)"""
    pass


class Text(object):
    """Base class for text files

    Parameters
    ----------
    cfg : tecs.gtb.config.Cfg
        configuration data
    obs : tecs.rinex.o.Obs
        an observation file
    """

    def __init__(self, cfg, obs):
        self.cfg = cfg
        self.obs = obs

        self.xyz = {}
        self.lbh = {}
        self.interval = obs.interval.value

        self.sampling_interval = 0.
        if cfg.samplingInterval:
            self.sampling_interval = cfg.samplingInterval.total_seconds()

        if self.interval > self.sampling_interval:
            self.sampling_interval = '{} (not used).'.format(
                self.sampling_interval)

        # input files dict
        # {sat: { 'sat_def': sat_def',
        #         'nav': nav_file,
        #         'fout': out_filename,
        #         'fobj': file }
        # }
        self.satellite = {}

        # output path
        self.path = None

    def write_data(self, sat, chunk):
        """write_data(sat, chunk) -> None

        Write a record into outfile using metadata.

        Parameters
        ----------
        sat : str
            satellite
        chunk : tuple
            list of values to write
        """
        logger = logging.getLogger(NAME + '.write_data')

        # outfile name
        marker = os.path.basename(self.obs.filename)[0:4]
        epoch = chunk[0]

        year = epoch.strftime('%Y')
        yday = epoch.strftime('%j')

        if not self.path:
            path = os.path.join(self.cfg.outDir, year, yday, marker)
            self.set_path(path)

            if not os.path.exists(self.path):
                os.makedirs(self.path)

        # - the name
        f_out = '%s_%s_%s_%s.%s' % (marker, sat, yday, year[2:], EXT)
        f_out = os.path.join(self.path, f_out)

        # new file
        if not self.satellite[sat]['fobj']:
            f_obj = open(f_out, 'wt')

            self.update_satellite(sat, fout=f_out)
            self.update_satellite(sat, fobj=f_obj)

            creation_time = datetime.datetime.now()
            creation_time = creation_time.strftime('%Y-%m-%d %H:%M:%S %Z')

            sources = '{}, {}'.format(
                self.obs.filename,
                (self.satellite[sat]['nav'] or 'None')
            )

            columns = re.sub(r"\(|\)|u'|'", '', str(self.cfg.recFields))

            comment = '# %s\n' % self.cfg.recFortranFormat
            comment = "# Columns: %s\n" % columns + comment
            comment = ("# datetime format: %s\n" %
                       self.cfg.datetimeFormat + comment)

            # - metadata[XYZ] = [ [epoch, (x, y, z)], ... ]
            comment = ("# Position (X, Y, Z): %s, %s, %s\n" %
                       self.xyz_latest + comment)

            comment = ("# Position (L, B, H): %s, %s, %s\n" %
                       self.lbh_latest + comment)

            comment = "# Site: %s\n" % marker + comment
            comment = ("# Sampling interval: %s\n" %
                       self.sampling_interval + comment)
            comment = ("# Interval: %s\n" %
                       self.interval + comment)
            comment = ("# Satellite: %s\n" %
                       self.satellite[sat]['sat_def'] + comment)
            comment = "# Sources: %s\n" % sources + comment
            comment = "# Created on %s\n" % creation_time + comment

            self.satellite[sat]['fobj'].write(comment)

        # write the data

        # all but the date
        vals = list(chunk[1:])
        if None in vals:
            nones = [i for (i, v) in enumerate(vals) if v is None]
            for i in nones:
                vals[i] = 0
        # an output record
        rec = None
        try:
            # format the date
            cur_datetime = epoch.strftime(self.cfg.datetimeFormat)
            cur_time = epoch.time()

            tsn = ((cur_time.hour * 3600 + cur_time.minute * 60
                    + cur_time.second + cur_time.microsecond * 1e-06) /
                   self.interval)

            # tsn must be int
            frac = tsn - int(tsn)
            if frac:
                if frac > 0.5:
                    tsn = math.ceil(tsn)
                else:
                    tsn = math.floor(tsn)

            tsn = int(tsn)

            hour = (
                ((cur_time.microsecond * 1e-6
                  + cur_time.second) / 60.
                 + cur_time.minute) / 60. + cur_time.hour)

            vals = [tsn, hour, cur_datetime] + vals
            rec = self.cfg.recFormat.format(*vals)

        except ValueError as err:
            msg = "Can't format out string %s (%s)." % (vals, err)
            logger.error(msg)

        self.satellite[sat]['fobj'].write(rec)

    def end_up(self):
        """end_up() -> None

        close the files and reset self.satellite.
        """
        logger = logging.getLogger(NAME + '.end_up')

        for sat in self.satellite:
            if self.satellite[sat]['fobj'] is None:
                msg = '{}: data handling of the {} satellite was skipped.'
                msg = msg.format(self.obs.filename, sat)
                logger.warning(msg)
            else:
                self.satellite[sat]['fobj'].close()

        # what if the xyz changed?
        if len(list(self.xyz.keys())) > 1:
            # self.write_positions()
            pass

        self.satellite = {}

    def update_satellite(self, sat, **kwargs):
        """update_satellite(self, **kwargs) -> None
        """
        logger = logging.getLogger(NAME + '.update_satellite')
        skeys = ['sat_def', 'nav', 'fout', 'fobj']

        err = set(kwargs.keys()).difference(set(skeys))
        if err:
            err = 'Unknown key(s) {} in kwargs.'.format(str(err))
            logger.error(err)
            raise TextError(err)

        if sat not in self.satellite:
            self.satellite[sat] = {}
            for k in skeys:
                self.satellite[sat][k] = None

        for k in kwargs:
            self.satellite[sat][k] = kwargs[k]

    def update_xyz(self, epoch, xyz):
        """update_xyz(epoch, xyz) -> None
        """
        logger = logging.getLogger(NAME + '.update_xyz')

        if epoch in self.xyz:
            msg = 'Duplicate XYZ value: {}, {}, {}.'
            msg = msg.format(self.obs.filename, epoch, xyz)
            logger.info(msg)

        self.xyz[epoch] = xyz

    def update_lbh(self, epoch, lbh):
        """update_lbh(epoch, lbh) -> None
        """
        logger = logging.getLogger(NAME + '.update_lbh')

        if epoch in self.lbh:
            msg = 'Duplicate lbh value: {}, {}, {}.'
            msg = msg.format(self.obs.filename, epoch, lbh)
            logger.info(msg)

        self.lbh[epoch] = lbh

    def set_path(self, path):
        """set_path(self, path) -> None
        """
        self.path = path

    # def write_positions(self):
    #     """write_positions(self) -> None
    #     """
    #     fout = '{}.pos'.format(
    #         os.path.basename(self.obs.filename)[:4]
    #     )
    #     fout = os.path.join(self.path, fout)
    #     fobj = open(fout, 'w')
    #
    #     comment = '# datetime X Y Z L B H\n'
    #     fobj.write(comment)
    #
    #     rec_fmt = ('{} ' +
    #                '{: 24.12f}' * 3 +
    #                '{: 24.12f}' * 3 +
    #                '\n')
    #
    #     for epoch in sorted(self.xyz.keys()):
    #         (x, y, z) = self.xyz[epoch]
    #         (l, b, h) = self.lbh[epoch]
    #         rec = rec_fmt.format(epoch, x, y, z, l, b, h)
    #         fobj.write(rec)
    #
    #     fobj.close()

    @property
    def xyz_latest(self):
        """xyz_latest(self) -> (x, y, z)
        """
        dates = sorted(self.xyz)
        return self.xyz[dates[-1]]

    @property
    def lbh_latest(self):
        """lbh_latest(self) -> (x, y, z)
        """
        dates = sorted(self.lbh)
        return self.lbh[dates[-1]]
