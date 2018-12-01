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

from PyQt5.QtGui import QColor


class Feature:
    """
    Base class for editor features.

    A `Feature` is something that can be registered in the Editor and add
    functionality (behavior or visually). All feature can be enabled
    or disabled through `Feaure.enabled` property.
    """

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if value != self._enabled:
            self._enabled = value
            self._state_changed(value)

    def __init__(self):
        self._enabled = False
        self._editor = None
        self.color = _Color()
        self.initialize()

    def initialize(self):
        pass

    def register(self, editor):
        self._editor = editor
        self.enabled = True

    def unregister(self):
        self.enabled = False
        self._editor = None

    def _state_changed(self, state: bool):
        if state:
            self.on_enabled()
        else:
            self.on_disabled()

    def on_enabled(self):
        """
        Do what you want when you enable the Feature.
        Common use would be to connect signals with the Editor.
        """

    def on_disabled(self):
        """
        Do what you want when you disable the Feature.
        Common use would be to disconnect signals with the Editor.
        """


class _Color:
    """Class to manage values related to color of a `Feature`"""

    @property
    def foreground(self):
        return self._foreground_color

    @foreground.setter
    def foreground(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self._foreground_color = color
        # self.update()

    @property
    def background(self):
        return self._background_color

    @background.setter
    def background(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self._background_color = color
        # self.update()

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        self._alpha = value
        # self.update()

    def __init__(self):
        self._foreground_color = QColor('white')
        self._background_color = QColor('black')
        self._alpha = 255


from ninja_ide.gui.editor.features.manager import FeatureManager  # noqa
from ninja_ide.gui.editor.features.current_line import CurrentLine  # noqa

__all__ = [
    'Feature',
    'FeatureManager',
    'CurrentLine'
]
