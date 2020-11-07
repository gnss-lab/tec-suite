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
File: 
Description: various procedures to work with navigation message
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from builtins import map

import re
import datetime
import logging

from tecs.rinex import nav_file
from tecs.rinex.futils import find_files
from tecs.rinex.label import SAT_SYS_GPS, SAT_SYS_GLO, SAT_SYS_GEO, \
    SAT_SYS_GAL, SAT_SYS_MIX, SAT_SYS_BDS
from tecs.sat import gps

NAME = 'tecs.rinex.nmutils'


class NMError(Exception):
    pass


def get_week_sec(epoch, epoch_start):
    """get_week_sec(epoch, epoch_start) -> gps_sec

    Parameters
    ----------
    epoch : datetime.datetime
    epoch_start : datetime.datetime

    Returns
    -------
    sec : float
        amount of seconds from the start of current GPS week.

    """
    cur_gps_epoch = epoch - epoch_start
    gps_week = cur_gps_epoch.days / 7.

    gps_sec = (gps_week - int(gps_week)) * (7 * 24 * 60 * 60)
    gps_sec += cur_gps_epoch.seconds

    return gps_sec


def compose_navigation_re(system, epoch):
    """

    Parameters
    ----------
    system : str
        satellite system code
    epoch : datetime.datetime
        date & time

    Returns
    --------
    re : re.Pattern
    """
    nav_id = {
        SAT_SYS_GPS: 'n',
        SAT_SYS_GLO: 'g',
        SAT_SYS_GEO: 'h',
        SAT_SYS_GAL: 'l',
        SAT_SYS_MIX: 'p'
    }

    classic_nav_tmpl = r'^(\w{{4}}){day}\w\.{year}{system}'

    modern_nav_tmpl = (
        '^(\w{{4}})'
        '\w{{5}}'
        '_\w_'
        '{year}{day}\d{{4}}'
        '_\w{{3}}'
        '(_\w{{3}})?'
        '_{system}N\.rnx'
    )

    modern_nav = modern_nav_tmpl.format(year=epoch.strftime('%Y'),
                                        day=epoch.strftime('%j'),
                                        system=system)

    if system in nav_id:
        # classic and modern name style
        classic_nav = classic_nav_tmpl.format(day=epoch.strftime('%j'),
                                              year=epoch.strftime('%y'),
                                              system=nav_id[system])

        re_str = '{classic} | {modern}'.format(classic=classic_nav,
                                               modern=modern_nav)
    else:
        # modern name only
        re_str = modern_nav

    return re.compile(re_str, (re.I | re.X))


def get_prior_file(files, priority):
    if not files:
        return None

    query = list(map(re.compile, priority, (re.I,) * len(priority)))
    for q in query:
        for f in files:
            if q.search(f):
                return f
    # TODO warn
    return files[0]


def load_navigation_message(paths, epoch, system, priority=None):
    """load_navigation_message(paths, epoch, system, priority=None)

    loads navigation message according to priority.

    Parameters
    ----------
    paths : list
        navigation files paths
    epoch : datetime.datetime
        epoch of the navigation message
    system : str
        satellite system
    priority : list
        list of 4-chars codes of the stations, it's a queue to find nav-file:
        we try to find priority[0] nav-message, then priority[1] and so on; if
        we found none, take the first found.
    """

    # navigation files corresponded to the date and the system
    nav_files = find_nav_files(paths, epoch, system)

    if not nav_files:
        nav_files = find_nav_files(paths, epoch, SAT_SYS_MIX)
        if not nav_files:
            no_file = "Can't find any navigation file for the '{}' on {}."
            raise NMError(no_file.format(system, epoch.strftime('%Y-%j')))

    found_nav = nav_files[0]

    # priority of the navigation files
    if priority:
        found_nav = get_prior_file(nav_files, priority)

    # could raise RinexError
    nav_obj = nav_file(found_nav)

    if system not in nav_obj.message:
        # FIXME should I try another nav-file?
        no_system = "Can't find any navigation message for the '{}' on {}."
        raise NMError(no_system.format(system, epoch.strftime('%Y-%j')))

    return nav_obj


def find_nav_files(paths, epoch, system):
    f_test = compose_navigation_re(system, epoch)
    nav_files = find_files(paths, f_test)
    return nav_files


def select_navigation_message(epoch, system, number, message, first_msg=False):
    """select_navigation_message(epoch, system, number, message,
            first_msg=False) -> seconds, ephemeris

    select and return appropriate navigation message from `message`.


    Parameters
    ---------
    epoch : datetime.datetime
    system : str
    number : int
    message : dict
    first_msg : bool, optional
        If the `first_msg` is True return the first message of
        the day.

    Returns
    -------
    seconds : float
        * GPS (and similar): seconds = week second;
        * GLONASS (and similar): seconds = dt.
    ephemeris : tuple
        ephemeris
    """
    logger = logging.getLogger(NAME + '.select_navigation_message')

    if system not in message:
        msg = 'There is no such system {sys} in the navigation message.'
        logger.info(msg.format(sys=system))
        return None

    if not message[system]:
        msg = 'There is no such navigation message.'
        logger.info(msg)
        return None

    if number not in message[system]:
        msg = 'There is no such satellite {sys}{sat} in the navigation ' \
              'message.'
        logger.info(msg.format(sys=system, sat=number))
        return None

    gps_way = (SAT_SYS_GPS, SAT_SYS_BDS, SAT_SYS_GAL)
    # glo_way = (SAT_SYS_GLO, SAT_SYS_GEO)

    epoch_start = None
    week_second = None
    if system == SAT_SYS_GPS:
        # GPS epoch started at 00:00:00 UT January 6, 1980
        epoch_start = gps.epoch_start

    elif system == SAT_SYS_BDS:
        # BDS epoch started at 00:00:00 UT January 1, 2006
        epoch_start = datetime.datetime(2006, 1, 1, 0, 0, 0)

    elif system == SAT_SYS_GAL:
        # Galileo epoch started at 00:00:00 GPS August 22, 1999
        # 13 leap seconds have been introduced into UTC since 1980
        epoch_start = datetime.datetime(1999, 8, 22, 0, 0, 13)

    if system in gps_way:
        week_second = get_week_sec(epoch, epoch_start)

    time = epoch.time()
    # number of seconds from start of the day
    obs_dt = datetime.timedelta(0, (time.hour * 60 ** 2 +
                                    time.minute * 60 +
                                    time.second))

    message_times = sorted(message[system][number].keys())

    # no need to look for
    if time in message[system][number]:
        if system in gps_way:
            t = week_second
        else:
            t = 0
        return t, message[system][number][time]

    # time deltas
    if system in (SAT_SYS_GPS, SAT_SYS_BDS):
        # the first message of the day
        if first_msg:
            return week_second, message[system][number][message_times[0]]

        # 2 hours GPS & BDS (?)
        dt = datetime.timedelta(0, 7200)

    # 3 hours Galileo
    elif system == SAT_SYS_GAL:
        dt = datetime.timedelta(0, 10800)

    elif system == SAT_SYS_GLO:
        # in 15 minutes range
        dt = datetime.timedelta(0, 900)

    elif system == SAT_SYS_GEO:
        # in 4 minutes and 16 seconds range
        dt = datetime.timedelta(0, 256)

    else:
        msg = 'Unsupported satellite system {}.'.format(system)
        raise Exception(msg)

    for mt in message_times:
        mt_dt = datetime.timedelta(0, (mt.hour * 60 ** 2 +
                                       mt.minute * 60 +
                                       mt.second))
        ier = 1
        if obs_dt > mt_dt:
            diff = obs_dt - mt_dt
        else:
            diff = mt_dt - obs_dt
            ier = -1

        if dt >= diff:
            diff = diff.total_seconds() * ier
            if system in gps_way:
                diff = week_second
            return diff, message[system][number][mt]

    return None
