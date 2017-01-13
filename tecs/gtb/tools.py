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

"""functions to use in tecs.__main__"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# import sys
# from tecs.rinex import label
from tecs.rinex.label import OBS_TYPE_LABELS

NAME = 'tecs.gtb.tools'


def parse_rec(rec):
    """parse_rec(rec) -> rec

    parse on observation record to retrieve values.

    Parameters
    ----------
    rec : dict
        an observation record

    Returns
    -------
    datum : dict
        {obs type: (obs value, LLI, signal strength), ...}

    """
    datum = {}
    obs_types = list(rec.keys())
    obs_types.sort()

    for ot_set in OBS_TYPE_LABELS:
        datum[ot_set] = (None,) * 3
        for ot in obs_types:
            if ot in ot_set:
                datum[ot_set] = rec[ot]
                obs_types.remove(ot)
                break

    return datum


# def ask(yes=False, msg=None):
#     """ask(yes=False, msg=None) -> True or raise SystemExit
#
#     Raise SystemExit(0) if the answer differs from 'y' or 'Y'.
#
#     Parameters
#     ----------
#     yes: bool
#         default answer
#     msg: str
#         message to ask
#
#     Returns
#     -------
#     If user answer differs from 'y/Y' raise SystemExit otherwise return True.
#     """
#     if yes:
#         return True
#
#     question = 'continue processing? [Y/n]:'
#
#     if msg:
#         msg = '{}\n{}'.format(msg, question)
#     else:
#         msg = question
#
#     print(msg, end=' ')
#     answer = sys.stdin.readline().rstrip()
#
#     if not answer or answer in 'yY':
#         return True
#     else:
#         raise SystemExit(0)
