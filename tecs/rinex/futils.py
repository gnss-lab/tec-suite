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
File: tecs.rinex.futils.py
Description: various utilities to work with directories, files and file names
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import io
from builtins import map
from builtins import str

import datetime
import logging
import os

import os.path
import re
import subprocess
import sys
import tempfile
from string import Template

NAME = 'tecs.rinex.futils'

RE_VER = re.compile(r'^\s*(\d+\.?\d*).*RINEX VERSION / TYPE$', re.I)

RE_MODERN_RINEX = re.compile(r'^(\w{4})\w{5}_[RSU]_(\d{4})(\d{3})\d{4}', re.I)
RE_CLASSIC_RINEX = re.compile(r'^(\w{4})(\d{3})\w{1,3}\.(\d{2})([odnmglphbc])',
                              re.I)

ARCH = r'\.z|\.gz'
CRD_EXT = '.xyz'

RE_Z = re.compile(r'(.*)\.(z|gz)$', re.I)
RE_CRX = re.compile(r'(.*)\.(\d{2}d|crx)', re.I)
RE_RNX = re.compile(r'(.*)\.(\d{2}o|rnx)', re.I)

# FIXME do I need this?
# RE_CLASSIC_NAV = re.compile(r'^(\w{4})(\d{3})\w\.(\d{2})([nglph])', re.I)
# Z_EXT = r'({})$'.format(ARCH)

GZIP = ['gzip', '-cd']
CRX2RNX = ['crx2rnx', '-']

if os.name == 'nt':
    GZIP[0] = r'apps/gzip.exe'
    CRX2RNX[0] = r'apps/crx2rnx.exe'


def _compose_res():
    obs_ext = r'({}|)$'.format(ARCH)

    classic_daily_obs = r'^\w{4}\d{3}\w\.\d{2}[od]'
    classic_fnmin_obs = r'^\w{4}\d{3}[a-x](00|15|30|45)\.\d{2}[od]'

    modern_obs = r'\w{9}_[RSU]_\d{11}_\w{3}_\w{3}_\wo\.(crx|rnx)'

    obs_tmpl = '{min}$ext|{day}$ext|{modern}$ext'.format(min=classic_fnmin_obs,
                                                         day=classic_daily_obs,
                                                         modern=modern_obs)
    obs_tmpl = Template(obs_tmpl)

    re_obs_str = obs_tmpl.substitute(ext=obs_ext)
    re_xyz_str = obs_tmpl.substitute(ext=CRD_EXT)

    re_obs_wo_ext_str = obs_tmpl.substitute(ext='')
    re_obs_wo_ext_str = '({})'.format(re_obs_wo_ext_str)

    return list(map(re.compile, (re_obs_str, re_xyz_str, re_obs_wo_ext_str),
                    (re.I,) * 3))


RE_OBS, RE_XYZ, RE_OBS_WO_EXT = _compose_res()


class UncompressError(Exception):
    """UncompressError(filename, msg)
    """

    def __init__(self, filename, msg):
        super(UncompressError, self).__init__()
        self.err_msg = "%s uncompress failed: %s" % (filename, msg)

    def __str__(self):
        return self.err_msg


def write_ascii_lines(src, dst):
    for line in src:
        line = line.decode(
            encoding='ascii',
            errors='ignore',
        )
        dst.write(line)


def expand_nav(filename):
    """expand_nav(filename) -> f_obj

    decompresses file using gzip (.z|.gz).

    Parameters
    ----------
    filename : str

    Returns
    -------
    f_obj : file
    """

    gzip = GZIP + [filename]

    if not RE_Z.match(filename):
        return open(filename)

    try:
        gzip_pipe = subprocess.Popen(
            gzip,
            stdout=subprocess.PIPE,
        )

        tmp_file = tempfile.TemporaryFile(mode='w+')
        write_ascii_lines(gzip_pipe.stdout, tmp_file)

        gzip_pipe.stdout.close()

        tmp_file.seek(0)
        return tmp_file

    except (OSError, ValueError) as err:
        msg = "can't uncompress the file (%s)." % err
        raise UncompressError(filename, msg)


def expand_obs(filename):
    """expand_obs(filename) -> f_obj

    decompresses and applies crx2rnx to the file.

    Parameters
    ----------
    filename : str

    Returns
    -------
    f_obj : file
    """

    gzip = GZIP + [filename]
    crx2rnx = CRX2RNX + [filename]

    f_bn = os.path.basename(filename)
    if not RE_OBS.match(f_bn):
        msg = "Not an observation rinex file."
        raise UncompressError(filename, msg)
    del f_bn

    tmp_file = tempfile.TemporaryFile(mode='w+')

    # rinex + .Z
    if RE_Z.match(filename):
        # gzip
        try:
            gzip_pipe = subprocess.Popen(
                gzip,
                stdout=subprocess.PIPE,
            )
        except OSError as err:
            msg = "can't execute gzip: %s" % str(err)
            raise UncompressError(filename, msg)

        # \d{2}o.Z
        if RE_RNX.match(filename):
            write_ascii_lines(gzip_pipe.stdout, tmp_file)

        # \d{2}d.Z
        elif RE_CRX.match(filename):
            try:
                crx2rnx_pipe = subprocess.Popen(
                    crx2rnx[0],
                    stdin=gzip_pipe.stdout,
                    stdout=subprocess.PIPE,
                )

            except (OSError, ValueError) as err:
                msg = "can't execute crx2rnx: %s" % str(err)
                raise UncompressError(filename, msg)

            write_ascii_lines(crx2rnx_pipe.stdout, tmp_file)
            crx2rnx_pipe.stdout.close()

        gzip_pipe.stdout.close()

        tmp_file.seek(0)
        return tmp_file

    # \d{2}d
    elif RE_CRX.match(filename):

        try:
            crx2rnx_pipe = subprocess.Popen(
                crx2rnx,
                stdout=subprocess.PIPE,
            )
        except (OSError, ValueError) as err:
            msg = "can't execute crx2rnx: %s" % str(err)
            raise UncompressError(filename, msg)

        write_ascii_lines(crx2rnx_pipe.stdout, tmp_file)

        crx2rnx_pipe.stdout.close()

        tmp_file.seek(0)
        return tmp_file

    # \d{2}o
    elif RE_RNX.match(filename):
        o_file = io.open(
            filename,
            'r',
            encoding='ascii',
            errors='ignore',
        )
        return o_file

    else:
        msg = "Not an observation rinex file."
        raise UncompressError(filename, msg)


def get_rinex_date(filename):
    """get_rinex_date(filename) -> date or None

    Parameters
    ----------
    filename : str
        path to the file.

    Returns
    -------
    date : datetime.date
    """
    logger = logging.getLogger(NAME + '.get_rinex_date')

    base_fn = os.path.basename(filename)
    year = None
    yday = None
    d_fmt = None

    match = RE_CLASSIC_RINEX.match(base_fn)
    if match:
        # classic
        year = match.group(3)
        yday = match.group(2)
        d_fmt = '%y-%j'
    else:
        match = RE_MODERN_RINEX.match(base_fn)
        if match:
            year = match.group(2)
            yday = match.group(3)
            d_fmt = '%Y-%j'

    if not match:
        msg = "Can't find out the date of the file: %s" % filename
        logger.warning(msg)
        return None

    d_str = '{}-{}'.format(year, yday)

    try:
        rinex_date = datetime.datetime.strptime(d_str, d_fmt)
    except ValueError as err:
        msg = "Can't find out the date of the file: {} ({})"
        msg = msg.format(filename, err)
        logger.warning(msg)
        return None

    return rinex_date.date()


def find_files(d_list, f_test):
    """get_files(d_list, f_test) -> None

    Parameters
    ----------
    d_list : list
    f_test : re.Pattern
    """
    f_bunch = []

    for d in d_list:
        fls = os.listdir(d)
        fls = [f for f in fls if f_test.match(f)]
        fls = [os.path.join(d, f) for f in fls]
        f_bunch += fls

    return f_bunch


def get_dir_list(line, delimiter=','):
    """get_dir_list(line, delimiter) -> list

    Parameters
    ----------
    line : str
    delimiter : str
        default ','
    """
    dlist = line.split(delimiter)

    dlist = [f.rstrip() for f in dlist]
    dlist = [f.lstrip() for f in dlist]

    return dlist


def find_xyz_file(fname):
    """find_xyz_file(fname) -> xyz_fname | None

    looks up xyz-file in the same dir with obs-file.

    Parameters
    ----------
    fname : str
        filename of the observation file.

    Returns
    -------
    xyz_fname : str
        corresponding xyz-file
    """
    logger = logging.getLogger(NAME + '.find_xyz_file')

    base_name = os.path.basename(fname)
    dir_name = os.path.dirname(fname)

    match = RE_OBS_WO_EXT.search(base_name)
    if not match:
        msg = '{} does not match {}.'.format(RE_OBS_WO_EXT, base_name)
        logger.error(msg)
        return None

    bare_name = match.group(1)
    xyz_file = '{file}{ext}'.format(file=os.path.join(dir_name, bare_name),
                                    ext=CRD_EXT)

    if not os.path.exists(xyz_file):
        return None

    msg = 'XYZ file found: {}'.format(xyz_file)
    logger.debug(msg)

    return xyz_file


def load_xyz_file(fname):
    """load_xyz_file(fname) -> xyz_data

    load coordinates from xyz-file.

    Parameters
    ----------
    fname : str

    Returns
    -------
    xyz_data : dict
    """
    logger = logging.getLogger(NAME + '.load_xyz_file')
    date_fmt = '%Y-%m-%d%H:%M:%S'

    xyz_data = {}

    fobj = open(fname)

    for rec in fobj:
        rec = rec.rstrip()
        if re.match(r'^\s*#.*', rec):
            continue
        if not rec:
            continue

        (cdate, ctime, x, y, z) = re.split(r'\s+', rec)
        epoch = datetime.datetime.strptime(cdate + ctime, date_fmt)

        if epoch in xyz_data:
            err = '{}: {} duplicate epoch'.format(fname, str(epoch))
            logger.info(err)

        try:
            xyz = [float(i) for i in (x, y, z)]
        except ValueError as err:
            err = '{}: {}'.format(fname, str(err))
            logger.error(err)

            sys.stderr.write('\n' + err + '\n')
            raise SystemExit(1)

        xyz_data[epoch] = tuple(xyz)

    fobj.close()

    return xyz_data
