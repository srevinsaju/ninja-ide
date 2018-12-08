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

import difflib
from PySide2.QtGui import QPainter
from PySide2.QtGui import QFontMetricsF
from PySide2.QtGui import QColor

from PySide2.QtCore import Slot
from PySide2.QtCore import QSize
from PySide2.QtCore import QTimer

from ninja_ide.gui.editor.side_area import SideWidget
from ninja_ide import resources


class TextChangeWidget(SideWidget):

    @property
    def unsaved_color(self):
        return self.__unsaved_color

    @unsaved_color.setter
    def unsaved_color(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.__unsaved_color = color

    @property
    def saved_color(self):
        return self.__saved_color

    @saved_color.setter
    def saved_color(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.__saved_color = color

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, ms):
        if ms != self.__delay:
            self.__delay = ms
            self._timer.setInterval(self.__delay)

    def __init__(self):
        SideWidget.__init__(self)
        # Delay Timer
        self._timer = QTimer(self)
        self._timer.setInterval(self.__delay)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.__on_text_changed)

    def initialize(self):
        self.__unsaved_markers = []
        self.__saved_markers = []
        self.__saved = False
        # Default properties
        self.__unsaved_color = QColor(
            resources.COLOR_SCHEME.get("editor.markarea.modified"))
        self.__saved_color = QColor(
            resources.COLOR_SCHEME.get("editor.markarea.saved"))
        self.__delay = 300

    def on_enabled(self):
        self.__text = self._editor.text
        self.__last_saved_text = self._editor.text

        # Connect textChanged signal to the timer
        # the __on_text_chaned slot is executed each '__delay' milliseconds
        self._editor.textChanged.connect(self._timer.start)
        self._editor.updateRequest.connect(self.update)
        self._editor.neditable.fileSaved.connect(self.__on_file_saved)

    @Slot()
    def __on_file_saved(self):
        self.__saved = True
        self.__last_saved_text = self._editor.text
        self.__saved_markers += list(self.__unsaved_markers)

    @Slot()
    def __on_text_changed(self):
        if self.__saved:
            self.__saved = False
            return
        self.__unsaved_markers.clear()
        old_text = self.__last_saved_text
        actual_text = self._editor.text
        matcher = difflib.SequenceMatcher(
            None,
            old_text.splitlines(),
            actual_text.splitlines()
        )
        for tag, _, _, j1, j2 in matcher.get_opcodes():
            if tag in ('insert', 'replace'):
                for lineno in range(j1, j2):
                    if lineno not in self.__unsaved_markers:
                        self.__unsaved_markers.append(lineno)
                    if lineno in self.__saved_markers:
                        self.__saved_markers.remove(lineno)

    def sizeHint(self):
        return QSize(2, 0)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        height = QFontMetricsF(self._editor.document().defaultFont()).height()
        width = self.sizeHint().width()
        for top, block_number, _ in self._editor.visible_blocks:
            for lineno in self.__unsaved_markers:
                if block_number == lineno:
                    painter.fillRect(
                        0, top, width, height, self.__unsaved_color)
            for lineno in self.__saved_markers:
                if block_number == lineno:
                    painter.fillRect(
                        0, top, width, height, self.__saved_color)
