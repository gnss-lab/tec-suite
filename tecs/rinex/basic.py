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
Description: 
"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from builtins import next
from builtins import object

from tecs.rinex.futils import get_rinex_date

NAME = 'tecs.rinex.basic'


def read_header(fobj):
    """read_header(fobj) -> header

    Parameters
    ----------
    fobj : file-like object

    Returns
    -------
    header : list
        header

    Notes
    -----
    Changes position in the file.
    """
    header = []
    for line in fobj:
        label = line[60:].rstrip()
        if label == 'END OF HEADER':
            break
        header.append(line)
    return header


class RinexError(Exception):
    def __init__(self, fname, msg):
        super(RinexError, self).__init__()
        self.err_msg = "%s (%s)" % (msg, fname)

    def __str__(self):
        return self.err_msg


class RinexFileTypeError(RinexError):
    def __init__(self, fname, rtype):
        msg = 'unknown file type: {}'.format(rtype)
        super(RinexFileTypeError, self).__init__(fname, msg)


class RinexValueError(RinexError):
    pass


class RinexReadError(RinexError):
    def __str__(self):
        msg = "[Reading error]: %s" % self.err_msg
        return msg


class Rinex(object):
    def __init__(self, f_obj, filename):
        """RINEX"""
        self._fobj = f_obj
        self.filename = filename
        self.filename_date = get_rinex_date(filename)

        # FIXME add `version` to __init__(), so one can define labels here.
        self.ver_type = None

    def _next_rec(self, f_obj):
        """_next_rec(iterator) -> line

        returns next line of the file.

        Parameters
        ----------
        f_obj : file-like object

        Returns
        -------
        line : str
            rstripped line of the file
        """
        try:
            rec = next(f_obj)
            rec = rec.rstrip()

        except StopIteration:
            msg = "unexpected end of the file."
            raise RinexError(self.filename, msg)

        return rec


class ObservationData(Rinex):
    def __init__(self, f_obj, filename):
        super(ObservationData, self).__init__(f_obj, filename)
        self.tofo = None
        self.xyz = (0., 0., 0.)
        self.interval = None

    def _parse_header(self, header):
        items = [self.ver_type, self.tofo, self.xyz, self.interval]

        for line in header:
            label = line[60:].rstrip()
            for i in items:
                if i.label == label:
                    i.value = line
                    items.remove(i)
                    break


class NavigationMessage(Rinex):
    """Base class for the navigation message.
    """

    def __init__(self, f_obj, filename):
        super(NavigationMessage, self).__init__(f_obj, filename)

    # FIXME join with ObservationData._parse_header
    def _parse_header(self, header):
        items = [self.ver_type]

        for line in header:
            label = line[60:].rstrip()
            for i in items:
                if i.label == label:
                    i.value = line
                    items.remove(i)
                    break
