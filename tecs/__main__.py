# !/usr/bin/env python
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

"""Reconstruction total electron value in the ionosphere using data of
the global navigation satellite systems such as GPS, GLONASS, etc.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os.path
import sys
import time
from builtins import next
from builtins import str

from tecs import version
from tecs.gtb.tools import parse_rec
from tecs.label import OUT_FILE_TEXT
from tecs.rinex import obs_file
from tecs.rinex.basic import RinexError
from tecs.rinex.futils import (
    UncompressError, RE_OBS, RE_XYZ, find_files,
    find_xyz_file, load_xyz_file
)
from tecs.rinex.label import (
    L1, L2, L5, P1, P2, C1, C5, C2, S1, S2, S5,
    SAT_SYS_GLO, SAT_SYS_GEO, SAT_SYS_GPS,
    SAT_SYS_MIX,
    TIME_SYS_GPS, SAT_SYS_BDS, L6, L7, L8, SAT_SYS_GAL,
    C6, C7, C8, LabelError
)
from tecs.rinex.nmutils import (
    load_navigation_message,
    select_navigation_message, NMError
)
from tecs.sat import gps, geo, glonass
from tecs.sat.common import compute_el_az, xyz2lbh_deg
from tecs.validity import eval_validity

START_TIME = time.time()

NAME = 'tecs'
VERSION = version

# Command line arguments
ARG_PARSER = argparse.ArgumentParser()

ARG_PARSER.add_argument(
    '-v', '--version',
    help="print the __main__.py version number and exit",
    action="store_true")

ARG_PARSER.add_argument(
    '-c', '--rcfile',
    help="specify a configuration file.")

ARG_PARSER.add_argument(
    '-y', '--yes',
    action='store_true',
    help="assume 'yes' is the answer."
)

ARG_PARSER.add_argument(
    '-q', '--quiet',
    action='store_true',
    help="suppress printing current datetime values during processing."
)

ARG_PARSER.add_argument(
    '--save-coordinates',
    action='store_true'
)

ARGS = ARG_PARSER.parse_args()

if ARGS.version:
    MSG = "tecs %s\n" % VERSION
    MSG += "Python %s" % sys.version
    print(MSG)
    sys.exit(0)

# Configuration
import tecs.gtb.config

CFG = tecs.gtb.config.CFG
if ARGS.rcfile:
    CFG.read_cfg(ARGS.rcfile)
else:
    CFG.read_cfg(tecs.gtb.config.DEFAULTS['cfg_file'])

# modules depended on configuration
import tecs.gtb.tec as tec

if CFG.outFileMode == OUT_FILE_TEXT:
    import tecs.dio.text

    D_WRITER = tecs.dio.text.Text
else:
    pass

# Logger
# change dir to use relative paths
os.chdir(os.path.dirname(CFG.cfg_file))

if not os.path.exists(CFG.outDir):
    os.makedirs(CFG.outDir)

LOGGER = logging.getLogger(NAME)
LOGGER.setLevel(logging.DEBUG)

LOG_LEVEL = getattr(logging, CFG.logLevel)

FILE_HANDLER = logging.FileHandler(CFG.logFile, mode='w')
FILE_HANDLER.setLevel(LOG_LEVEL)

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.WARNING)

FORMATTER = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
FILE_HANDLER.setFormatter(FORMATTER)

FORMATTER = logging.Formatter('[%(levelname)s] %(message)s')
CONSOLE_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(CONSOLE_HANDLER)

del CONSOLE_HANDLER, FILE_HANDLER, FORMATTER, LOG_LEVEL

# Supported satellite systems
SUPPORTED_SYSTEMS = (SAT_SYS_GPS,
                     SAT_SYS_GLO,
                     SAT_SYS_GEO,
                     SAT_SYS_BDS,
                     SAT_SYS_GAL)


def main():
    """main()
    """
    logger = logging.getLogger(NAME + '.main')
    logger_error_count = 0

    stdout = sys.stdout
    stdout.write('Trying to find observation files...')  # [Verbose]
    stdout.flush()

    obs_files = find_files(CFG.obsDir, RE_OBS)
    obs_files.sort()

    msg = 'obs-files found: {}'.format(str(obs_files))
    logger.debug(msg)
    print('done (%s).' % len(obs_files))

    if not obs_files:
        msg = "Can't find any observation file in '%s'." % CFG.obsDir
        print(msg)
        raise SystemExit(0)

    total_files = len(obs_files)

    xyz_files = find_files(CFG.obsDir, RE_XYZ)
    if xyz_files:
        msg = 'xyz-files found: {}'.format(str(xyz_files))
        logger.debug(msg)

    # navigation file according to the date and satellite system;
    # (for comment proposes)
    nav_file = {}

    # function to compute the satellite's XYZ according to the sat system
    get_sat_xyz = {
        SAT_SYS_GPS: gps.compute_sat_xyz,
        SAT_SYS_BDS: gps.compute_sat_xyz,
        SAT_SYS_GAL: gps.compute_sat_xyz,
        SAT_SYS_GLO: glonass.compute_sat_xyz,
        SAT_SYS_GEO: glonass.compute_sat_xyz
    }

    # XYZ of the satellite according to the
    #  sat system, sat number, date and time
    sat_xyz = {}

    # GLONASS freq (depends on ephemeris)
    glo_freq = {}

    # FIXME get into shape or remove
    coordinates_filename = 'coordinates.txt'
    crds_file = None
    if ARGS.save_coordinates:
        crds_file = open(coordinates_filename, 'w')

    for (f_num, o_file) in enumerate(obs_files):

        print("%s [%s/%s]: " % (o_file, f_num + 1, total_files))
        stdout.flush()

        try:
            print("- reading...", end='')
            stdout.flush()
            obs = obs_file(o_file)
        except (RinexError, UncompressError) as err:
            msg = "%s" % err
            logger.error(msg)
            logger_error_count += 1
            continue

        if obs.ver_type.value[2] not in SUPPORTED_SYSTEMS + (SAT_SYS_MIX,):
            msg = '{} it is not supported satellite system; skipped.'
            msg = msg.format(obs.ver_type.value[2])
            logger.warning(msg)
            continue

        # [Verbose]
        print("done.")
        print("- processing...")

        time_sys = obs.tofo.value[1]
        if time_sys != TIME_SYS_GPS:
            msg = "{} - system time: '{}'."
            msg = msg.format(obs.filename, time_sys)
            logger.error(msg)
            logger_error_count += 1
            continue

        # initial value of the XYZ and LBH
        (x, y, z) = obs.xyz.value
        (l, b, h) = xyz2lbh_deg(x, y, z)

        # FIXME get into shape or remove
        if ARGS.save_coordinates:
            rec = '{site}; {lon}; {lat}\n'.format(
                site=os.path.basename(obs.filename)[0:4],
                lon=l,
                lat=b
            )
            crds_file.write(rec)
            continue

        xyz_data = {}
        xyz_cur_file = None
        if xyz_files:
            # FIXME try to find in xyz_files, not in a directory
            xyz_cur_file = find_xyz_file(obs.filename)
            if xyz_cur_file:
                xyz_data = load_xyz_file(xyz_cur_file)

        # data writer instance
        writer = D_WRITER(CFG, obs)

        writer.update_xyz(obs.tofo.value[0], (x, y, z))
        writer.update_lbh(obs.tofo.value[0], (l, b, h))

        sampling_interval = None
        if CFG.samplingInterval:
            if CFG.samplingInterval.total_seconds() > obs.interval.value:
                sampling_interval = CFG.samplingInterval
        last_epoch = None

        # nav message for the current obs file
        nav_message = {}

        record_iter = obs.read_records()
        while 1:
            try:
                epoch, sat, rec = next(record_iter)
            except StopIteration:
                break
            except RinexError as err:
                msg = "%s - %s" % (o_file, str(err))
                logger.error(msg)
                logger_error_count += 1
                continue

            # [Verbose]
            if not ARGS.quiet:
                erase_msg = '\b' * 30
                stdout.write(erase_msg)
                stdout.write(str(epoch))
                stdout.flush()

            system, number = sat[0], int(sat[1:])
            obs_date, obs_time = epoch.date(), epoch.time()

            if system not in SUPPORTED_SYSTEMS:
                continue

            if obs_date != obs.filename_date:
                msg = "{} - epoch {} does not match the file date ({})."
                msg = msg.format(obs.filename, str(obs_date),
                                 str(obs.filename_date))
                logger.info(msg)
                continue

            if sampling_interval:
                if not last_epoch:
                    last_epoch = epoch

                if last_epoch != epoch:
                    dt = epoch - last_epoch
                    if dt < sampling_interval:
                        continue
                    last_epoch = epoch

            if obs_date not in nav_file:
                nav_file[obs_date] = {}

            if system not in nav_message:
                nav_message[system] = None
                nav_file[obs_date][system] = None

                try:
                    nm = load_navigation_message(CFG.navDir, epoch, system,
                                                 CFG.navPriority[system])
                except RinexError as err:
                    logger.error(str(err))
                    continue
                except NMError as err:
                    # warnings.warn(str(err))
                    logger.warning(str(err))
                    continue

                if nm:
                    nav_message[system] = nm.message[system]
                    nav_file[obs_date][system] = nm.filename

                del nm

            # satellite XYZ
            if system not in sat_xyz:
                sat_xyz[system] = {}

            if number not in sat_xyz[system]:
                sat_xyz[system][number] = {}

            if obs_date not in sat_xyz[system][number]:
                sat_xyz[system][number][obs_date] = {}

            if obs_time not in sat_xyz[system][number][obs_date]:
                sat_xyz[system][number][obs_date][obs_time] = None
                eph = select_navigation_message(epoch,
                                                system, number,
                                                nav_message, first_msg=True)
                if eph is not None:
                    dt, eph = eph

                    try:
                        sat_xyz[system][number][obs_date][obs_time] = \
                            get_sat_xyz[system](eph, dt)
                    except ArithmeticError as err:
                        # FIXME common thing: verbose function?
                        msg = "{}, {} - ArithmeticError: {} ({})"
                        msg = msg.format(nav_file[obs_date][system],
                                         obs.filename, err, epoch)
                        logger.error(msg)
                        logger_error_count += 1
                        continue

                    # GLONASS freq
                    if system == SAT_SYS_GLO:
                        k = eph[7]

                        if number not in glo_freq:
                            glo_freq[number] = {}

                        if obs_date not in glo_freq[number]:
                            glo_freq[number][obs_date] = {}

                        if obs_time not in glo_freq[number][obs_date]:
                            glo_freq[number][obs_date][obs_time] = \
                                (glonass.F1(k), glonass.F2(k), k)

                        # health bit
                        if eph[3] != 0:
                            msg = "{} - {} sat {}: health bit = '{}'"
                            msg = msg.format(nav_file[obs_date][system],
                                             epoch, sat, eph[3])
                            logger.info(msg)

            # site position can be changed during parsing the file via
            # 1) xyz file
            if xyz_data and epoch in xyz_data:
                (x, y, z) = xyz_data[epoch]
                (l, b, h) = xyz2lbh_deg(x, y, z)

                msg = '{} set xyz to {} according to {}.'
                msg = msg.format(obs.filename, xyz_data[epoch], xyz_cur_file)
                logger.debug(msg)

            # 2) 'APPROX POSITION XYZ' records
            elif (x, y, z) != obs.xyz.value:
                (x, y, z) = obs.xyz.value
                (l, b, h) = xyz2lbh_deg(x, y, z)

                msg = '{} set xyz to {} according to obs file properties.'
                msg = msg.format(obs.filename, obs.xyz.value)
                logger.debug(msg)

            if (x, y, z) != writer.xyz_latest:
                writer.update_xyz(epoch, (x, y, z))
                writer.update_lbh(epoch, (l, b, h))

            # elevation and azimuth
            cur_sat_xyz = sat_xyz[system][number][obs_date][obs_time]
            if cur_sat_xyz is None:
                if not CFG.navIgnoreAbsence:
                    continue

                if system == SAT_SYS_GLO:
                    continue

                cur_sat_xyz = (0., 0., 0.)
                el, az = 0., 0.

            else:
                try:
                    el, az = compute_el_az((x, y, z), cur_sat_xyz)
                except ArithmeticError as err:
                    msg = "{}, {} - ArithmeticError: {} ({})"
                    msg = msg.format(nav_file[obs_date][system],
                                     obs.filename, err, epoch)
                    logger.error(msg)
                    logger_error_count += 1
                    continue

            if el < 0:
                err = "el = {} ({}, {}, {}, {}) "
                err = err.format(el, obs.filename,
                                 nav_file[obs_date][system],
                                 epoch, sat)
                logger.info(err)
                continue

            # frequencies
            f1, f2, f5, f6, f7, f8 = (None,) * 6

            # satellite definition (outfile comments)
            sat_def = sat

            # GLONASS
            if system == SAT_SYS_GLO:
                f1, f2, k = glo_freq[number][obs_date][obs_time]

                # k
                sat_def = '%s (k = %s)' % (sat, k)

            # GPS
            elif system == SAT_SYS_GPS:
                f1 = gps.F1
                f2 = gps.F2
                f5 = gps.F5

            # GEO
            elif system == SAT_SYS_GEO:
                f1 = geo.F1
                f5 = geo.F5

                # PRN = PRN + 100
                sat_def = int(sat[1:])
                sat_def = "%s (PRN %s)" % (sat, (sat_def + 100))

            # BDS
            elif system == SAT_SYS_BDS:
                # TODO move to appropriate place
                f2 = 1561.098 * 1e6
                f7 = 1207.14 * 1e6
                f6 = 1268.52 * 1e6

            elif system == SAT_SYS_GAL:
                # TODO move to appropriate place
                f1 = 1575.42 * 1e6
                f5 = 1176.45 * 1e6
                f6 = 1278.75 * 1e6
                f7 = 1207.14 * 1e6
                # noinspection PyUnusedLocal
                f8 = 1191.795 * 1e6

            else:
                msg = '{} - Unknown satellite system.'.format(obs.filename)
                logger.info(msg)
                continue

            # parsing observables
            ds = parse_rec(rec)

            # calculate TEC
            # - via L1&L2
            tec_l1l2 = tec.compute_via_l(ds[L1][0], ds[L2][0], f1, f2, 0)

            # - via L1&L5
            tec_l1l5 = tec.compute_via_l(ds[L1][0], ds[L5][0], f1, f5, 0)

            # - via L2&L5
            tec_l2l5 = tec.compute_via_l(ds[L2][0], ds[L5][0], f2, f5, 0)

            # L2 L6
            tec_l2l6 = tec.compute_via_l(ds[L2][0], ds[L6][0], f2, f6, 0)

            # L2 L7
            tec_l2l7 = tec.compute_via_l(ds[L2][0], ds[L7][0], f2, f7, 0)

            # L6 L7
            tec_l6l7 = tec.compute_via_l(ds[L6][0], ds[L7][0], f6, f7, 0)

            # TODO
            # L1 L6
            # L1 L7
            # L1 L8

            # L5 L6
            # L5 L7
            # L5 L8

            # L6 L7
            # L7 L8

            # L7 L8

            # - via P1&P2
            tec_p1p2 = tec.compute_via_p(
                ds[P1][0], ds[P2][0],
                f1, f2)

            # - via C1&P2
            tec_c1p2 = tec.compute_via_p(
                ds[C1][0], ds[P2][0],
                f1, f2)

            # - via L1&C1
            tec_l1c1 = tec.compute_via_l1_c1(
                ds[L1][0], ds[C1][0],
                f1)

            # - via L2&C2
            tec_l2c2 = tec.compute_via_l1_c1(
                ds[L2][0], ds[C2][0],
                f2)
            
            # - via L8&C8
            tec_l8c8 = tec.compute_via_l1_c1(
                ds[L8][0], ds[C8][0],
                f8)
            
            # - via C1&C5
            tec_c1c5 = tec.compute_via_p(
                ds[C1][0], ds[C5][0],
                f1, f5)

            # - via C1&C2
            tec_c1c2 = tec.compute_via_p(
                ds[C1][0], ds[C2][0],
                f1, f2)

            # - via C2&C5
            tec_c2c5 = tec.compute_via_p(
                ds[C2][0], ds[C5][0],
                f2, f5)

            # via C2&C6
            tec_c2c6 = tec.compute_via_p(
                ds[C2][0], ds[C6][0],
                f2, f6)

            # via C2&C7
            tec_c2c7 = tec.compute_via_p(
                ds[C2][0], ds[C7][0],
                f2, f7)

            # via C6&C7
            tec_c6c7 = tec.compute_via_p(
                ds[C6][0], ds[C7][0],
                f6, f7)

            # validity
            if obs.VERSION < 3:
                obs_types = obs.properties['obs types']
            else:
                obs_types = obs.sys_n_obs.value[system]

            validity_types = []

            for o_type in list(rec.keys()):
                if rec[o_type][0]:
                    validity_types.append(o_type)

            if ds[L1][1]:
                if ds[L1][1] & 1:
                    validity_types.append('LLI1')
            if ds[L2][1]:
                if ds[L2][1] & 1:
                    validity_types.append('LLI2')
            if ds[L5][1]:
                if ds[L5][1] & 1:
                    validity_types.append('LLI5')

            try:
                validity = eval_validity(obs_types, validity_types)
            except LabelError as err:
                msg = '{} - {}'.format(obs.filename, str(err))
                logger.warning(msg)
                continue

            # output record
            data_chunk = (

                epoch,

                el, az,

                ds[P1][0], ds[P1][1],
                ds[P2][0], ds[P2][1],
                tec_p1p2,

                ds[L1][0], ds[L1][1],
                ds[L2][0], ds[L2][1],
                tec_l1l2,

                validity,

                ds[S1][0], ds[S1][1],
                ds[S2][0], ds[S2][1],
                ds[S5][0], ds[S5][1],

                ds[C1][0], ds[C1][1],
                ds[C2][0], ds[C2][1],

                tec_c1p2,
                tec_l1c1,

                ds[L5][0], ds[L5][1],
                tec_l1l5,

                ds[C5][0], ds[C5][1],
                tec_c1c5,

                tec_l2l5,
                tec_c1c2,
                tec_c2c5,

                cur_sat_xyz[0],
                cur_sat_xyz[1],
                cur_sat_xyz[2],

                x,
                y,
                z,

                l,
                b,
                h,

                tec_l2l6,
                tec_l2l7,
                tec_l6l7,

                tec_c2c6,
                tec_c2c7,
                tec_c6c7,
                tec_l2c2,
                tec_l8c8,
            )

            dc_len = len(data_chunk)
            def_len = len(CFG.formatDef) - 2
            msg = 'dc_len != def_len (CFG.formatDef)'
            assert dc_len == def_len, msg

            if sat not in writer.satellite:
                writer.update_satellite(
                    sat,
                    sat_def=sat_def,
                    nav=nav_file[obs_date][system]
                )

            writer.write_data(sat, data_chunk)

        writer.end_up()

        print()
        print('done.')

    if crds_file:
        crds_file.close()

    return logger_error_count


def run():
    error_count = main()

    errors_fmt = '\nThere are some errors, check out the log-file: {}.'
    total_time_fmt = 'Total processing time: {: .3f} min.'

    if error_count != 0:
        errors = errors_fmt.format(CFG.logFile)
        print(errors)

    end_time = time.time()

    total_time = (end_time - START_TIME) / 60.
    print(total_time_fmt.format(total_time))


if __name__ == '__main__':
    run()
