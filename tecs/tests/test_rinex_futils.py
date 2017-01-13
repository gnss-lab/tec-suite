#!/usr/bin/env python
# coding=utf8
"""
File: 
Description: 
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from builtins import object

import datetime

from tecs.rinex.futils import get_rinex_date

NAME = "tecs.tests.test_rinex_futils"


class TestRINEXFutils(object):

    def __init__(self):
        pass

    def test_get_rinex_date(self):
        rfile = [
            'HKSL00HKG_R_20161000000_01D_30S_CN.rnx.gz',
            'zimj1000.16n'
        ]

        for f in rfile:
            d = get_rinex_date(f)
            print(d)
            assert d == datetime.date(2016, 4, 9)
