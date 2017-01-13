#!/usr/bin/env python
# coding=utf8
"""
File: test_rinex_common.py
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from nose.plugins.attrib import attr
from nose.tools import assert_raises

from tecs.rinex.common import validate_epoch

NAME = 'test_rinex_common'
VERSION = 0.1


@attr('rinex.common')
def test_validate_epoch():
    """validate_epoch
    """
    epoch = (
        [2000, 1, 1, 1, 0, 0, 0],
        [1988, 1, 2, 3, 61, 14, 1250],  # min == 61
        [92, 11, 16, 7, 34, 60, 0],  # sec == 60
        [2, 11, 16, 7, 120, 0, 0]  # min == 120
    )

    test_epoch = (
        [2000, 1, 1, 1, 0, 0, 0],
        [1988, 1, 2, 4, 1, 14, 1250],
        [1992, 11, 16, 7, 35, 0, 0],
        [2002, 11, 16, 9, 0, 0, 0]
    )

    for i, test in enumerate(test_epoch):
        test = datetime.datetime(*test)
        result = validate_epoch(epoch[i])

        err = '{} != {}'.format(test, result)
        assert test == result, err

    epoch = [1999, 6, 8, 21, 0, 121, 0]

    with assert_raises(ValueError):
        validate_epoch(epoch)
