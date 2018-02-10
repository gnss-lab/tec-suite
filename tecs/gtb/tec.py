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
Calculate a TEC value using pseudorange and phase data.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import tecs.gtb.config
import tecs.label as lbl

NAME = 'tecs.gtb.tec'
LOGGER = logging.getLogger(NAME)

# speed of light, m/s
C = 299792458

CFG = tecs.gtb.config.CFG

# TEC values to calculate (according to the CFG)
TEC2CALC = [i for i in CFG.recFields if i in lbl.R_TEC_ALL]

# для удобства
TEC_P = (lbl.R_TEC_P1P2, lbl.R_TEC_C1P2, lbl.R_TEC_C1C5, lbl.R_TEC_C1C2,
         lbl.R_TEC_C2C5, lbl.R_TEC_C2C6, lbl.R_TEC_C2C7, lbl.R_TEC_C6C7)

TEC_L = (lbl.R_TEC_L1L2, lbl.R_TEC_L1L5, lbl.R_TEC_L2L5,
         lbl.R_TEC_L2L6, lbl.R_TEC_L2L7, lbl.R_TEC_L6L7)


def tec_factor(f1, f2):
    """tec_factor(f1, f2) -> the factor

    TEC factor to calculate TEC, TECU.

    Parameters
    ----------
    f1 : float
    f2 : float

    Returns
    -------
    factor : float

    """
    return 1 / 40.308 * (f1 ** 2 * f2 ** 2) / (f1 ** 2 - f2 ** 2) * 1.0e-16


# noinspection PyUnusedLocal
def plug_func(*args, **kwargs):
    return None


def compute_on_demand_p(func):
    """ """
    calc_me = [t for t in TEC_P if t in TEC2CALC]

    if CFG.outFileModeText and calc_me:
        return func
    else:
        return plug_func


def compute_on_demand_l(func):
    """ """
    calc_me = [t for t in TEC_L if t in TEC2CALC]
    if CFG.outFileModeText and calc_me:
        return func
    else:
        return plug_func


def compute_on_demand_l1_c1(func):
    """ """
    if CFG.outFileModeText and (
            lbl.R_TEC_L1C1 in TEC2CALC or
            lbl.R_TEC_L2C2 in TEC2CALC
    ):
        return func
    else:
        return plug_func


@compute_on_demand_p
def compute_via_p(p1, p2, f1, f2):
    """compute_via_p(p1, p2, f1, f2) -> tec

    calculate a TEC value using pseudorange data.

    Parameters
    ----------
    p1 : float
        f1 pseudorange value, meters
    p2 : float
        f2 pseudorange value, meters
    f1 : float
        f1 frequency, Hz
    f2 : float
        f2 frequency, Hz
    """

    if not f1:
        return None

    if not f2:
        return None

    # TEC P
    tec = None

    if p1 and p2:
        tec = tec_factor(f1, f2) * (p2 - p1)

    return tec


@compute_on_demand_l
def compute_via_l(l1, l2, f1, f2, l0=0):
    """compute_via_l(l1, l2, l0, f1, f2) -> tec

    reconstruct a TEC value using phase data.

    Parameters
    ----------
    l1 : float
        f1 phase value, whole cycles
    l2 : float
        f2 phase value, whole cycles
    f1 : float
        f1 frequency, Hz
    f2 : float
        f2 frequency, Hz
    l0 : float
        initial phase, Hz; default = 0
    """

    if not f1:
        return None

    if not f2:
        return None

    tec = None

    if l1 and l2:
        # c/f = λ 
        tec = tec_factor(f1, f2) * (C / f1 * l1 - C / f2 * l2) - l0

    return tec


@compute_on_demand_l1_c1
def compute_via_l1_c1(l1, c1, f1):
    """compute_via_l1_c1(l1, c1, f1) -> tec:

    reconstruct a TEC value using pseudorange and phase data (f1).

    Parameters
    ----------
    l1 : float
        f1 phase, whole cycles
    c1 : float
        f1 pseudorange (C/A-code), meters
    f1 : float
        f1 frequency value, Hz
    """

    if not f1:
        return None

    tec = None

    if c1 and l1 and f1:
        # c/f = λ                                           TECU
        tec = 0.5 * f1 ** 2 / 40.308 * (c1 - l1 * C / f1) * 1.0e-16

    return tec
