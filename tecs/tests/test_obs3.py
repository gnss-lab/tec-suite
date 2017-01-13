#!/usr/bin/env python
# coding=utf8
"""
File: 
Description: 
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import object

import datetime

import nose

from io import StringIO
import tecs.rinex.v3.o as obs_v3

NAME = 'test_obs3'

# noinspection PyPep8
RINEX = """     3.02           OBSERVATION DATA    M                   RINEX VERSION / TYPE
sbf2rin-9.3.3                           20160402 000422 LCL PGM / RUN BY / DATE
CEBR                                                        MARKER NAME
13408M001                                                   MARKER NUMBER
AUTOMATIC           ESA/ESOC                                OBSERVER / AGENCY
3001288             SEPT POLARX4        2.9.0               REC # / TYPE / VERS
5163                SEPCHOKE_MC     NONE                    ANT # / TYPE
  4846664.9180  -370195.2000  4116929.5260                  APPROX POSITION XYZ
        0.1780        0.0000        0.0000                  ANTENNA: DELTA H/E/N
G   18 C1C L1C D1C S1C C1W S1W C2W L2W D2W S2W C2L L2L D2L  SYS / # / OBS TYPES
       S2L C5Q L5Q D5Q S5Q                                  SYS / # / OBS TYPES
E   16 C1C L1C D1C S1C C5Q L5Q D5Q S5Q C7Q L7Q D7Q S7Q C8Q  SYS / # / OBS TYPES
       L8Q D8Q S8Q                                          SYS / # / OBS TYPES
S    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES
R   12 C1C L1C D1C S1C C2P L2P D2P S2P C2C L2C D2C S2C      SYS / # / OBS TYPES
C    8 C1I L1I D1I S1I C7I L7I D7I S7I                      SYS / # / OBS TYPES
G L1C  0.00000                                              SYS / PHASE SHIFTS
G L2W  0.00000                                              SYS / PHASE SHIFTS
G L2L  0.00000                                              SYS / PHASE SHIFTS
G L5Q  0.00000                                              SYS / PHASE SHIFTS
E L1C  0.00000                                              SYS / PHASE SHIFTS
E L5Q  0.00000                                              SYS / PHASE SHIFTS
E L7Q  0.00000                                              SYS / PHASE SHIFTS
E L8Q  0.00000                                              SYS / PHASE SHIFTS
S L1C  0.00000                                              SYS / PHASE SHIFTS
R L1C  0.00000                                              SYS / PHASE SHIFTS
R L2P  0.00000                                              SYS / PHASE SHIFTS
R L2C  0.00000                                              SYS / PHASE SHIFTS
C L1I  0.00000                                              SYS / PHASE SHIFTS
C L7I  0.00000                                              SYS / PHASE SHIFTS
    30.000                                                  INTERVAL
  2016     4     1     0     0    0.0000000     GPS         TIME OF FIRST OBS
  2016     4     1    23    59   30.0000000     GPS         TIME OF LAST OBS
    82                                                      # OF SATELLITES
 C1C    0.000 C2C    0.000 C2P    0.000                     GLONASS COD/PHS/BIS
DBHZ                                                        SIGNAL STRENGTH UNIT
 23 R01  1 R02 -4 R03  5 R04  6 R05  1 R06 -4 R07  5 R08  6 GLONASS SLOT / FRQ #
    R09 -6 R10 -7 R11  0 R13 -2 R14 -7 R15  0 R16 -1 R17  4 GLONASS SLOT / FRQ #
    R18 -3 R19  3 R20  2 R21  4 R22 -3 R23  3 R24  2        GLONASS SLOT / FRQ #
                                                            END OF HEADER
> 2016 04 01 00 00  0.0000000  0 11
S25  37448170.553 7 196791495.99007       -73.470 7        44.250
E19  24758282.971 7 130105642.65907      1831.182 7        45.250    24758286.101 7  97156842.79007      1367.476 7        43.250    24758282.806 7  99691361.28707      1403.148 7        44.750    24758283.924 7  98424109.04307      1385.315 7        47.000
G11  21791273.856 8 114513931.93508      2440.270 8        48.250    21791273.360 5        35.500    21791271.849 5  89231629.32405      1901.513 5        35.500
S23  38540487.727 7 202530969.44207         2.482 7        45.000
G27  20704920.061 8 108805158.64308     -1230.079 8        51.750    20704919.731 7        46.750    20704921.451 7  84783282.15307      -958.505 7        46.750    20704921.429 8  84783288.15608      -958.448 8        48.500    20704922.100 8  81250655.40208      -918.552 8        53.750
G16  23465369.983 6 123311412.23906     -3631.856 6        40.750    23465369.393 4        25.250    23465369.764 4  96086853.53804     -2830.014 4        25.250
G10  21739947.482 8 114244210.42708     -1923.109 8        49.000    21739947.442 6        40.250    21739948.600 6  89021463.30006     -1498.526 6        40.250    21739948.103 7  89021465.31007     -1498.476 7        44.750    21739947.634 8  85312238.74408     -1436.067 8        49.750
G22  22112704.804 7 116203057.96307      2914.521 7        47.250    22112703.839 5        35.750    22112701.030 5  90547828.16305      2271.059 5        35.750
G08  20392732.576 8 107164564.50608       808.276 8        52.000    20392732.380 7        46.000    20392733.837 7  83504885.13907       629.823 7        46.000    20392734.508 8  83504892.15208       629.806 8        48.500    20392733.685 9  80025521.39809       603.596 9        54.250
G07  24802224.251 6 130336569.51806     -1978.890 6        39.000    24802224.234 3        19.250    24802221.890 3 101560969.62803     -1541.974 3        19.250    24802222.503 5 101560962.62605     -1542.276 5        34.500
E12  24073210.368 8 126505634.40108       679.055 8        48.250    24073211.517 8  94468534.55808       507.079 8        49.750    24073208.342 8  96932915.41408       520.322 8        50.500    24073209.411 8  95700721.99108       513.701 8        53.250
> 2016 04 01 00 00  0.0000000  1  2
G11  21777362.813 8 114440830.79908      2433.035 8        48.250    21777362.322 6        36.000    21777361.029 6  89174667.40706      1895.871 6        36.000
S23  38540472.469 7 202530893.97807         2.623 7        45.000
>                              4 11
    67                                                      # OF SATELLITES
G   16   C1C   L1C   D1C   S1C   C2S   L2S   D2S   S2S   C2WCOMMENT
         L2W   D2W   S2W   C5Q   L5Q   D5Q   S5Q            COMMENT
   G01   756   756   756   756   755   755   755   755   756PRN / # OF OBS
         756   756   756   756   756   756   756            PRN / # OF OBS
   G02  1070  1070  1070  1070     0     0     0     0  1066PRN / # OF OBS
        1066  1066  1066     0     0     0     0            PRN / # OF OBS
   G03  1222  1221  1221  1222  1214  1214  1214  1214  1219PRN / # OF OBS
        1219  1219  1219  1217  1217  1217  1217            PRN / # OF OBS
   G05  1060  1058  1058  1060  1053  1053  1053  1053  1054PRN / # OF OBS
        1054  1054  1054     0     0     0     0            PRN / # OF OBS
>                              4  1
  0000000.0000  0000000.0000  0000000.0000                  APPROX POSITION XYZ
> 2016 04 01 00 00 15.0000000  0  2
G11  21777362.813 8 114440830.79908      2433.035 8        48.250    21777362.322 6        36.000    21777361.029 6  89174667.40706      1895.871 6        36.000
S23  38540472.469 7 202530893.97807         2.623 7        45.000
"""


class TestObs3(object):
    def __init__(self):
        self.fobj = StringIO(RINEX)
        self.obs = None
        self.err_msg = 'Wrong value: {result} (expected: {standard});' \
                       ' index={i}'

    def setup(self):
        self.obs = obs_v3.Obs3(self.fobj, 'cebr0920.16o')

    def test__parse_header(self):
        """test__parse_header"""
        sys_obs = dict(
            G=('C1C', 'L1C', 'D1C', 'S1C', 'C1W', 'S1W', 'C2W', 'L2W', 'D2W',
               'S2W', 'C2L', 'L2L', 'D2L', 'S2L', 'C5Q', 'L5Q', 'D5Q', 'S5Q'),
            E=('C1C', 'L1C', 'D1C', 'S1C', 'C5Q', 'L5Q', 'D5Q', 'S5Q', 'C7Q',
               'L7Q', 'D7Q', 'S7Q', 'C8Q', 'L8Q', 'D8Q', 'S8Q'),
            S=('C1C', 'L1C', 'D1C', 'S1C'),
            R=('C1C', 'L1C', 'D1C', 'S1C', 'C2P', 'L2P', 'D2P', 'S2P', 'C2C',
               'L2C', 'D2C', 'S2C'),
            C=('C1I', 'L1I', 'D1I', 'S1I', 'C7I', 'L7I', 'D7I', 'S7I')
        )

        assert self.obs.ver_type.value == (3.02, 'O', 'M')
        assert self.obs.xyz.value == (4846664.9180, -370195.2000, 4116929.5260)
        assert self.obs.interval.value == 15.0
        assert self.obs.sys_n_obs.value == sys_obs
        assert self.obs.tofo.value == (
            datetime.datetime(2016, 4, 1, 0, 0, 0, 0),
            'GPS')

    def test__parse_obs_record(self):
        """test__parse_obs_record"""
        record = 'C05  40498966.534 5 210888798.39505       -39.173 5' \
                 '        35.750    40498964.477 6 163072617.03306' \
                 '       -30.366'

        sat = 'C05'
        values = (
            (40498966.534, 0, 5),
            (210888798.395, 0, 5),
            (-39.173, 0, 5),
            (35.750, 0, 0),
            (40498964.477, 0, 6),
            (163072617.033, 0, 6),
            (-30.366, 0, 0),
            (0.0, 0, 0)
        )

        test_sat, test_values = self.obs._parse_obs_record(record)

        msg = "{test_sat} != {sat}".format(test_sat=test_sat, sat=sat)
        assert test_sat == sat, msg

        msg = "{test_values} != {values}".format(test_values=test_values,
                                                 values=values)
        assert test_values == values, msg

    def test__parse_epoch_record(self):
        """test__parse_epoch_record"""
        epoch_record = '> 2016 01 01 01 29 30.0000000  0 23' \
                       '      01.000001000000'

        standard = (
            datetime.datetime(2016, 1, 1, 1, 29, 30, 0),
            0,
            23,
            datetime.timedelta(0, 1, 1)
        )

        result = self.obs._parse_epoch_record(epoch_record)

        for i, item in enumerate(standard):
            msg = self.err_msg.format(result=result[i], standard=item, i=i)
            assert item == result[i], msg

    def test__handle_event(self):
        epoch = datetime.datetime(2016, 4, 1)
        epoch_flag = 4

        # noinspection PyPep8
        special_records = [
            '  0000000.0000  0000000.0000  0000000.0000                  APPROX POSITION XYZ\n',
            '    60.200                                                  INTERVAL\n'
        ]

        self.obs._handle_event(epoch, epoch_flag, special_records)

        assert self.obs.interval.value == 60.2
        assert self.obs.xyz.value == (0., 0., 0.)

    def test_read_records(self):
        """
        E   16 C1C L1C D1C S1C C5Q L5Q D5Q S5Q
        C7Q L7Q D7Q S7Q C8Q L8Q D8Q S8Q
        """
        s_dt = datetime.datetime(2016, 4, 1, 0, 0)
        s_sat = ('S25', 'E19')
        s_obs = (

            {'C1C': (37448170.553, 0, 7),
             'L1C': (196791495.990, 0, 7),
             'D1C': (-73.47, 0, 7),
             'S1C': (44.250, 0, 0)},

            {'C1C': (24758282.971, 0, 7),
             'L1C': (130105642.659, 0, 7),
             'D1C': (1831.182, 0, 7),
             'S1C': (45.250, 0, 0),
             'C5Q': (24758286.101, 0, 7),
             'L5Q': (97156842.790, 0, 7),
             'D5Q': (1367.476, 0, 7),
             'S5Q': (43.250, 0, 0),
             'C7Q': (24758282.806, 0, 7),
             'L7Q': (99691361.287, 0, 7),
             'D7Q': (1403.148, 0, 7),
             'S7Q': (44.750, 0, 0),
             'C8Q': (24758283.924, 0, 7),
             'L8Q': (98424109.043, 0, 7),
             'D8Q': (1385.315, 0, 7),
             'S8Q': (47.000, 0, 0)}
        )

        i = 0
        for rec in self.obs.read_records():
            if i > 1:
                break

            assert rec[0] == s_dt
            assert rec[1] == s_sat[i]
            assert rec[2] == s_obs[i]

            i += 1

    def test__det_interval(self):
        self.obs._det_interval()
        assert self.obs.interval.value == 15., self.obs.interval.value

    # def _det_filename_date(self):
    #     assert False

    def test__handle_power_failure(self):
        raise nose.SkipTest

    def test__det_data_chunks(self):
        raise nose.SkipTest
