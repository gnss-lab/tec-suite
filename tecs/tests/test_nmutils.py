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

import datetime

from tecs.rinex.label import SAT_SYS_GPS, SAT_SYS_GAL

from tecs.rinex.nmutils import compose_navigation_re

NAME = 'tecs.tests.test_nmutils'


def test_compose_navigation_re():
    nav_file_v2 = 'cebr1000.16l.Z'
    nav_file_v3 = 'CEBR00ESP_R_20161000000_01D_EN.rnx.gz'

    epoch = datetime.datetime(2016, 4, 9)
    system = SAT_SYS_GAL

    re_nav = compose_navigation_re(system, epoch)

    assert re_nav.match(nav_file_v2)
    assert re_nav.match(nav_file_v3)

    epoch = datetime.datetime(2016, 4, 10)
    system = SAT_SYS_GPS

    re_nav = compose_navigation_re(system, epoch)

    assert not re_nav.match(nav_file_v2)
    assert not re_nav.match(nav_file_v3)

    nav_file_v3_df = 'ISTP00RUS_R_20160010000_01H_50Z_GN.rnx'
    epoch = datetime.datetime(2016, 1, 1)
    system = SAT_SYS_GPS

    re_nav = compose_navigation_re(system, epoch)
    assert re_nav.match(nav_file_v3_df)
