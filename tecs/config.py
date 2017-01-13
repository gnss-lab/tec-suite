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

""" Configuration
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from builtins import object

import sys
import re


class CfgError(Exception):
    """ CfgError(Exception)
    """

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class CfgValueError(CfgError):
    """CfgValueError(Exception)
    """

    def __init__(self, fname, param, value):
        msg = "Config file: {}. Value is wrong '{}' = '{}'\n"
        msg = msg.format(self.args)

        super(CfgValueError, self).__init__(msg)


class Configuration(object):
    """Base class for the configuration

    can parse configuration files with 'param = value' syntax. Read params
    become the instance attributes.
    """

    def __init__(self, defaults):
        """"""
        self.settings = None
        self.set_defaults(defaults)

        self.cfg_file = None

        # рег. выражения
        self._re_q = re.compile(r"['\"](.*)['\"]")
        self._re_range = re.compile(r'\((\S+),\s*(\S+)\)')
        self._re_bool = re.compile(r'True', re.I)

        # проверка вхождения в диапазон
        self._in_r = lambda v, r: (r[0] <= v <= r[1]) or False

    def _get_bool(self, bstr):
        """_get_bool(str) -> True|False
        """

        if self._re_bool.match(bstr):
            return True
        else:
            return False

    def _get_str(self, in_str):
        """_get_str(str) -> str
        """

        if self._re_q.match(in_str):
            # pylint: disable=eval-used
            return eval('r' + in_str)
        else:
            return in_str

    def _get_path(self, in_str):
        """ _get_path(str) -> str
        """

        in_str = re.sub(r'\\', r'/', in_str)
        return self._get_str(in_str)

    # def _set_range(self, attr, a_range):
    #     """_set_range(attr, range) -> None
    #
    #     converts str('(str, str)') into tuple(float, float)
    #     """
    #     match = self._re_range.match(a_range)
    #
    #     if not match:
    #         raise CfgValueError(self.cfg_file, attr, a_range)
    #
    #     try:
    #         lft = float(match.group(1))
    #         rgt = float(match.group(2))
    #         setattr(self, attr, (lft, rgt))
    #     except ValueError:
    #         raise CfgValueError(self.cfg_file, attr, a_range)

    def set_defaults(self, defaults):
        """set_defaults(defaults)
        """
        self.settings = defaults.copy()
        for (name, val) in list(self.settings.items()):
            setattr(self, name, val)

    def read_cfg(self, filename):
        """read_cfg(filename)
        """
        self.cfg_file = filename

        try:
            fh = open(filename, 'r')
        except IOError as err:
            err_msg = "Can't open configuration file {}. {}\n"
            err_msg = err_msg.format(filename, str(err))
            raise CfgError(err_msg)

        for line in fh:

            line = line.rstrip()
            line = re.sub(r'#.*', '', line)

            if not len(line):
                continue

            (name, val) = re.split('=', line, 2)

            # убираем пробелы
            name = re.sub(r'\s+', '', name)

            val = re.sub(r'^\s+', '', val)
            val = re.sub(r'\s+$', '', val)

            if len(val):
                if name in self.settings:
                    setattr(self, name, val)
                    self.settings[name] = val
                else:
                    warn = 'Ignoring unknown parameter: <%s>\n' % name
                    sys.stderr.write(warn)
            else:
                warn = 'Ignoring empty value: %s = <%s>\n' % (name, val)
                sys.stderr.write(warn)

        fh.close()
