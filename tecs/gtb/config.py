#!/usr/bin/evn python
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
config.py: configuration of the tecs
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import os
import os.path
import re

from tecs.config import Configuration
from tecs.rinex.common import sec2sec_ms
from tecs.rinex.futils import get_dir_list
from tecs.label import R_DATETIME, R_ELEVATION, R_AZIMUTH, R_TEC_L1L2, R_ALL
from tecs.label import R_VALIDITY, OUT_FILE_TEXT
from tecs.rec import Rec

from tecs.rinex.label import SAT_SYS_GPS, SAT_SYS_GLO, SAT_SYS_GEO, \
    SAT_SYS_BDS, SAT_SYS_GAL

NAME = 'tecs.gtb.config'
LOGGER = logging.getLogger(NAME)

# Defaults
DRF = '{}, {}, {}, {}, {}'
DRF = DRF.format(R_DATETIME, R_ELEVATION, R_AZIMUTH, R_TEC_L1L2, R_VALIDITY)

DEFAULTS = dict(
    cfg_file='./tecs.cfg',
    obsDir='./obs',
    navDir='./nav',
    outDir='./out',
    navPriorityGPS=[],
    navPriorityGLO=[],
    navPriorityGEO=[],
    samplingInterval=0,
    navIgnoreAbsence=False,
    elNanValue=-9999.,
    azNanValue=-9999.,
    outFileMode=OUT_FILE_TEXT,
    recFields=DRF,
    datetimeFormat='%Y-%j %H:%M:%S',
    logLevel='DEBUG',
    logFile='tecs.log'
)


class CfgError(Exception):
    """"""

    def __init__(self, msg):
        super(CfgError, self).__init__()
        self.err_msg = "Cfg: %s" % (msg,)

    def __str__(self):
        return self.err_msg


class Cfg(Configuration, Rec):
    """Cfg(defaults) -> config.Cfg
    """

    def __init__(self, defaults):
        """ """
        self.cfg_file = None

        self.obsDir = None
        self.navDir = None
        self.outDir = None

        self.outFileMode = None
        self.outFileModeText = None

        self.recFields = None
        self.recFortranFormat = None
        self.datetimeFormat = None

        self.navPriorityGPS = None
        self.navPriorityGLO = None
        self.navPriorityGEO = None

        self.navPriority = {
            SAT_SYS_GPS: (),
            SAT_SYS_GLO: (),
            SAT_SYS_GEO: (),
            SAT_SYS_BDS: (),
            SAT_SYS_GAL: ()
        }

        self.navIgnoreAbsence = None
        self.elNanValue = None
        self.azNanValue = None

        self.logLevel = None
        self.logFile = None

        self.recFormat = ''
        self.formatDef = None

        self.samplingInterval = None

        self.defaults = defaults
        Configuration.__init__(self, defaults)

        # output format self.formatDef
        Rec.__init__(self)

    def read_cfg(self, filename):
        """read_cfg(filename) -> None


        read configuration file; do some checks and conversions.

        Parameters
        ----------
        filename : str
            filename to read.
        """
        self.__init__(self.defaults)
        Configuration.read_cfg(self, filename)

        self.logLevel = self.get_log_level(self.logLevel)

        tmp = self._get_str(self.recFields)
        tmp = tmp.lower()
        tmp = re.sub(r'\s+', '', tmp)
        tmp = tmp.split(',')

        self.recFields = tuple(tmp)
        del tmp

        self.obsDir = get_dir_list(self.obsDir)
        self.navDir = get_dir_list(self.navDir)
        self.outDir = self._get_path(self.outDir)

        self.datetimeFormat = self._get_str(self.datetimeFormat)

        self.outFileMode = self.outFileMode.lower()
        if self.outFileMode == OUT_FILE_TEXT:
            self.outFileModeText = True
        else:
            err = "outFileMode = {}; outFileMode should be {}."
            err = err.format(self.outFileMode, OUT_FILE_TEXT)
            raise CfgError(err)

        cur_datetime = datetime.datetime.now()
        cur_datetime = cur_datetime.strftime(self.datetimeFormat)
        self.formatDef['datetime']['fortran'] = 'A%s' % len(cur_datetime)

        self.compose_rec_format(self.recFields)

        # turn nav files priorities into the list
        if self.navPriorityGPS:
            self.navPriorityGPS = re.sub(r'\s+', '', self.navPriorityGPS)
            self.navPriorityGPS = re.split(',', self.navPriorityGPS)
            self.navPriority[SAT_SYS_GPS] = tuple(self.navPriorityGPS)

        if self.navPriorityGLO:
            self.navPriorityGLO = re.sub(r'\s+', '', self.navPriorityGLO)
            self.navPriorityGLO = re.split(',', self.navPriorityGLO)
            self.navPriority[SAT_SYS_GLO] = tuple(self.navPriorityGLO)

        if self.navPriorityGEO:
            self.navPriorityGEO = re.sub(r'\s+', '', self.navPriorityGEO)
            self.navPriorityGEO = re.split(',', self.navPriorityGEO)
            self.navPriority[SAT_SYS_GEO] = tuple(self.navPriorityGEO)

        self.navIgnoreAbsence = self._get_bool(self.navIgnoreAbsence)

        self.logFile = os.path.join(self.outDir, self.logFile)

        si = float(self.samplingInterval)
        si_sec, si_microseconds = sec2sec_ms(si)
        if si:
            self.samplingInterval = datetime.timedelta(
                days=0,
                seconds=si_sec,
                microseconds=si_microseconds
            )
        else:
            self.samplingInterval = None

    @staticmethod
    def get_log_level(log_level):
        """ get_log_level(log_level) -> log_level

        check and return a log level eg 'DEBUG', 'INFO'... to use that level
        with the logging.

        Parameters
        ----------
        log_level : str
        """

        all_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        upper_level = log_level.upper()

        if upper_level not in all_levels:
            msg = "Unknown log level: '%s'" % log_level
            raise CfgError(msg)

        return upper_level

    def compose_rec_format(self, fields):
        """compose_rec_format(fields) -> rec_format
        """

        tmp = list(fields)

        rec_format = ''
        fortran_format = ''

        # если есть метка 'all' - включаем все возможные поля
        if R_ALL in tmp:
            tmp = list(self.formatDef.keys())
            tmp.sort()
            self.set_rec_fields(tmp)

        # the first value - without space
        first = None
        try:
            first = tmp.pop(0)
            rec_format += self.formatDef[first]['format']
            fortran_format += self.formatDef[first]['fortran']
        except KeyError:
            msg = 'wrong format value: <%s>' % first
            raise CfgError(msg)

        # and the others with space at the start of the value string
        for i in tmp:
            try:
                rec_format += " %s" % self.formatDef[i]['format']
                fortran_format += ',1X,%s' % self.formatDef[i]['fortran']
            except KeyError:
                msg = 'wrong format value: <%s>' % i
                raise CfgError(msg)

        rec_format += '\n'
        fortran_format = '(%s)' % fortran_format

        del tmp

        self.set_rec_format(rec_format)
        self.set_rec_fortran_format(fortran_format)

    def set_rec_format(self, fmt):
        """set_rec_format(fmt) -> None"""
        self.recFormat = fmt

    def set_rec_fortran_format(self, fmt):
        """set_rec_fortran_format(fmt) -> None"""
        self.recFortranFormat = fmt

    def set_rec_fields(self, fields):
        """set_rec_fields(fields) -> None"""
        self.recFields = tuple(fields)


# FIXME WTF?
CFG = Cfg(DEFAULTS)
