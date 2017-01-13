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

"""Validity functions
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tecs.rinex.label import LLI1, LLI2, \
    C1, L1, L2, P1, P2, S1, S2, D1, D2, D5, \
    C2, C5, L5, S5, LLI5, get_label

BIT_SET = {
    LLI1: 2 ** 0,
    LLI2: 2 ** 1,
    C1: 2 ** 2,
    L1: 2 ** 3,
    L2: 2 ** 4,
    P1: 2 ** 5,
    P2: 2 ** 6,
    S1: 2 ** 7,
    S2: 2 ** 8,
    D1: 2 ** 9,
    D2: 2 ** 10,
    D5: 2 ** 11,
    C2: 2 ** 12,
    C5: 2 ** 13,
    L5: 2 ** 14,
    S5: 2 ** 15,
    LLI5: 2 ** 16
}


def set_bits(obs_types):
    value = 0
    for o_type in obs_types:
        label = get_label(o_type)
        if label in BIT_SET:
            value |= BIT_SET[label]
    return value


def eval_validity(obs_types, validity_types):
    """eval_validity(obs_types, validity_types)

    Parameters
    ----------
    obs_types : list
        expected observation types list
    validity_types : list
        actual epoch's type list

    Returns
    -------
    validity : int
    """
    standard = set_bits(obs_types)
    actual_value = set_bits(validity_types)

    return standard ^ actual_value
