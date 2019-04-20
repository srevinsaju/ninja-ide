# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.
"""Test command line arguments"""

import shlex
import pytest

from ninja_ide.core import cliparser


@pytest.fixture
def command_line_parser():
    return cliparser.cmd_parser()


def test_parser_args_valid(command_line_parser):
    cmd = (
        'f1.py f2.py',
        '--projects some_project',
        '--projects pr1 pr2',
        '--plugins p1'
        '--plugins p1 p2 p3',
        '--stylesheet my_qss.qss',
        '--verbose'
    )
    for line in cmd:
        cmdline = shlex.split(line)
        command_line_parser.parse_args(cmdline)


def test_parser_args_invalid(command_line_parser):
    cmd = (
        '--invalid-arg blabla',
        '--stylesheet',
        '--projects'
    )
    for line in cmd:
        cmdline = shlex.split(line)
        with pytest.raises(SystemExit):
            command_line_parser.parse_args(cmdline)
