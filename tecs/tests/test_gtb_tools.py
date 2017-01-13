#!/usr/bin/env python
# coding=utf8
"""
File: test_gtb_tools.py
Description: test suite for tec.gtb.tools
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import os.path
import tempfile

from nose.plugins.attrib import attr

from tecs.rinex.futils import find_xyz_file, load_xyz_file

NAME = 'test_gtb_tools'
VERSION = 0.1


@attr('gtb.tools')
def test_find_xyz_file():
    """gtb.tools.find_xyz_file()
    """
    files = (
        ('usud0700.11d.Z', 'usud0700.11d.xyz'),
        ('usud0700.11o', 'usud0700.11o.xyz'),
        ('usud070a00.11o', 'usud070a00.11o.xyz')
    )

    for (obs_name, xyz_name) in files:

        tdir = tempfile.mkdtemp()

        obs_file = os.path.join(tdir, obs_name)
        xyz_file = os.path.join(tdir, xyz_name)

        with open(xyz_file, 'w') as fobj:
            fobj.write('# xyz file\n')
        f_file = find_xyz_file(obs_file)
        assert f_file, 'XYZ file for the {} ({}) not found.'.format(
            os.path.basename(obs_file),
            os.path.basename(xyz_file)
        )


@attr('gtb.tools')
def test_load_xyx_file():
    """gtb.tools.load_xyz_file()
    """
    test_data = {
        datetime.datetime(2011, 3, 11, 5): (-3855263.0771,
                                            3427432.6022,
                                            3741020.3066),
        datetime.datetime(2011, 3, 11, 5, 0, 30): (-3855263.0833,
                                                   3427432.6068,
                                                   3741020.3148)
    }

    comment = '''# Site: USUD
# Datum: IGS08
# datetime, x(meters), y(meters), z(meters)

'''
    fobj = tempfile.NamedTemporaryFile(mode='wt')

    fobj.write(comment)

    for dt in sorted(test_data):
        rec = '{} {} {} {}\n'.format(dt, *test_data[dt])
        fobj.write(rec)

    fobj.seek(0)

    loaded_data = load_xyz_file(fobj.name)

    for epoch in test_data:
        test = test_data[epoch]
        loaded = loaded_data[epoch]

        msg = '{} != {}'.format(test, loaded)
        assert test == loaded, msg
