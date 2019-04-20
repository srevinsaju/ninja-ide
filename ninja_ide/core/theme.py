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

"""Module responsible for loading the NINJA theme style"""
import os

from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import json_manager


NINJA_THEME_EXTENSION = '.ninjatheme'


class _NTheme:

    @classmethod
    def new(cls, *args, **kwargs):
        """Create a Ninja Theme"""

        ninja_theme = cls()
        return ninja_theme

    def __init__(self, file_path=None):
        self._file_path = file_path
        self._palette_colors = {}
        self._editor_style_name = ""
        self._stylesheet_name = ""
        self._name = ""
        structure = {}
        if file_path is not None:
            structure = json_manager.read_json(file_path)
        if structure:
            self._name = structure['Name']
            self._editor_style_name = structure['EditorStyle']
            self._palette_colors = structure['Palette']
            self._stylesheet_name = structure['StyleSheet']

    @property
    def display_name(self) -> str:
        return self._name or 'Unnamed'

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def editor_style(self) -> str:
        """Preferred editor style for the theme"""
        return self._editor_style_name

    @property
    def stylesheet(self) -> str:
        return self._stylesheet_name

    def set_up_palette(self):
        if not self._palette_colors:
            return
        palette = QPalette()
        for role, color in self._palette_colors.items():
            color = QColor(color)
            color_group = QPalette.All
            color_role = getattr(palette, role)
            palette.setBrush(color_group, color_role, color)
        app = QApplication.instance()
        app.setPalette(palette)


def available_themes() -> list:
    all_temes = []
    for theme_dir in (resources.NINJA_THEMES, resources.NINJA_THEMES_DOWNLOAD):
        themes = file_manager.get_files_from_folder(theme_dir, NINJA_THEME_EXTENSION)
        for theme in themes:
            all_temes.append(os.path.join(theme_dir, theme))
    return all_temes


# FIXME: improve this when settings is complete functional


def load_theme_from_file(filename='/home/gabo/projects/ninja-ide/ninja_ide/extensions/theme/ninja_dark.ninjatheme'):
    theme = _NTheme(filename)
    theme.set_up_palette()
    print("Name: {}".format(theme.display_name))
    print("Editor: {}".format(theme.editor_style))


def load_theme():
    # Read from settings
    # If not, set default
    pass
