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
Common things to use in rinex.*
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime


def validate_epoch(epoch):
    """validate_epoch(epoch) -> datetime

    do some checks:

    - sometimes the seconds or minutes value >= 60, to return datetime.datetime
      we need to check this;
    - converts YY to YYYY (datetime.datetime threats 92 and 1992 in different
      ways.

    Parameters
    ----------
    epoch : list
        epoch = [year, month, day, hour, min, sec, microsec]

    Returns
    -------
    datetime : datetime.datetime
    """
    epoch = epoch[:]

    # YY -> YYYY
    if epoch[0] < 100:
        if epoch[0] >= 89:
            epoch[0] += 1900
        elif epoch[0] < 89:
            epoch[0] += 2000

    delta = datetime.timedelta(0)

    # epoch[-2] - seconds; epoch[-3] - minutes
    # we do all calculation in seconds so we use multiplier
    for i, ier in [(-2, 1), (-3, 60)]:
        if 60 <= epoch[i] <= 120:
            sec = (epoch[i] - 59) * ier
            delta += datetime.timedelta(seconds=sec)
            epoch[i] = 59

    epoch = datetime.datetime(*epoch) + delta

    return epoch


def sec2sec_ms(sec):
    """sec2sec_ms(sec) -> sec, microsec

    Parameters
    ----------
    sec : float

    Returns
    -------
    seconds : int
    microsec : int
    """
    microsec = (sec - int(sec)) * 1e+6
    microsec = float("%.1f" % microsec)

    return int(sec), int(microsec)
