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
rinex
"""
from __future__ import unicode_literals

from tecs.rinex.basic import RinexError
from tecs.rinex.futils import RE_VER, GZIP, CRX2RNX, expand_obs, expand_nav
from tecs.rinex.header import RinexVersionType

from tecs.rinex.v2.o import Obs2, Obs21, Obs211
from tecs.rinex.v3.o import Obs3, Obs301, Obs302, Obs303

from tecs.rinex.v2.n import Nav2, Nav21, Nav211
from tecs.rinex.v3.n import Nav3, Nav301, Nav302, Nav303


def obs_file(filename):
    """obs_file(filename) -> Obs

    Parameters
    ----------
    filename : str
        path to observation file

    Returns
    -------
        rinex.(v2|v3).o.ObsN
    """
    f_obj = expand_obs(filename)

    ver_line = f_obj.readline()
    ver_line = ver_line.rstrip()
    match = RE_VER.match(ver_line)

    # в начало
    f_obj.seek(0)

    if not match:
        err = "can't find out rinex version \n'%s'" % ver_line
        raise RinexError(filename, err)

    ver = match.group(1)
    rinex_version = float(ver)

    rnx_cls = {
        2.00: Obs2,
        2.10: Obs21,
        2.11: Obs211,
        3.00: Obs3,
        3.01: Obs301,
        3.02: Obs302,
        3.03: Obs303
    }

    if rinex_version in rnx_cls:
        return rnx_cls[rinex_version](f_obj, filename)
    else:
        err = 'unknown rinex version: %s' % rinex_version
        raise RinexError(filename, err)


def nav_file(filename):
    """nav_file(filename) -> Nav

        Parameters
        ----------
        filename : str
            path to navigation file

        Returns
        -------
            rinex.(v2|v3).n.NavN
        """
    f_obj = expand_nav(filename)
    version = f_obj.readline()

    try:
        version = float(version[:9])
    except ValueError:
        msg = 'not a RINEX file {}'.format(filename)
        raise RinexError(filename, msg)

    f_obj.seek(0)

    nav_cls = {
        2.00: Nav2,
        2.01: Nav2,
        2.10: Nav21,
        2.11: Nav211,
        3.00: Nav3,
        3.01: Nav301,
        3.02: Nav302,
        3.03: Nav303,
        3.04: Nav303
    }

    if version in nav_cls:
        return nav_cls[version](f_obj, filename)
    else:
        err = 'unsupported RINEX version: {}.'.format(version)
        raise RinexError(filename, err)
