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

import sys
import os
import signal

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QPalette, QColor
# from PySide2.QtCore import Qt
# from PySide2.QtCore import QCoreApplication

from ninja_ide.core import cliparser

PR_SET_NAME = 15
PROCNAME = b"ninja-ide"


def run_ninja():
    """First obtain the execution args and create the resources folder."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Change the process name only for linux yet
    is_linux = sys.platform == "darwin" or sys.platform == "win32"
    if is_linux:
        try:
            import ctypes
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            # Set the application name
            libc.prctl(PR_SET_NAME, b"%s\0" % PROCNAME, 0, 0, 0)
        except OSError:
            print("The process couldn't be renamed'")
    filenames, projects_path, extra_plugins, linenos, verbose = cliparser.parse()
    # Create the QApplication object before using the
    # Qt modules to avoid warnings
    app = QApplication(sys.argv)
    from ninja_ide import resources
    # from ninja_ide.core import settings
    resources.create_home_dir_structure()
    # Load Logger
    from ninja_ide.tools.logger import NinjaLogger
    NinjaLogger.set_up(verbose)

    # Load Settings
    # settings.load_settings()
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, settings.HDPI)
    # if settings.CUSTOM_SCREEN_RESOLUTION:
    #     os.environ["QT_SCALE_FACTOR"] = settings.CUSTOM_SCREEN_RESOLUTION
    # from ninja_ide import ninja_style
    theme = resources.load_theme()
    palette = load_pallete(theme['palette'])
    app.setPalette(palette)
    # Stylesheet
    stylesheet_fname = os.path.join(resources.NINJA_QSS, theme['stylesheet'])
    with open(stylesheet_fname + '.qss') as fp:
        qss = fp.read()
    app.setStyleSheet(qss)
    # app.setStyle(ninja_style.NinjaStyle(resources.load_theme()))

    from ninja_ide import gui
    # Start the UI
    gui.start_ide(app, filenames, projects_path, extra_plugins, linenos)

    sys.exit(app.exec_())


def load_pallete(theme):
    qpalette = QPalette()
    for role, color in theme.items():
        qcolor = QColor(color)
        color_group = QPalette.All
        if role.endswith("Disabled"):
            role = role.split("Disabled")[0]
            color_group = QPalette.Disabled
        elif role.endswith("Inactive"):
            role = role.split("Inactive")[0]
            qcolor.setAlpha(90)
            color_group = QPalette.Inactive
        color_role = getattr(qpalette, role)
        qpalette.setBrush(color_group, color_role, qcolor)
    return qpalette
