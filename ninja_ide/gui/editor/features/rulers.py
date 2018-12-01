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

from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QFontMetricsF

from ninja_ide.gui.editor.features import Feature


class Ruler(Feature):

    @property
    def positions(self) -> list:
        return self.__positions

    @positions.setter
    def positions(self, pos: list):
        if pos != self.__positions:
            self.__positions.clear()
            self.__positions.extend(pos)
            self._editor.viewport().update()

    def on_enabled(self):
        self._editor.painted.connect(self._draw)

    def on_disabled(self):
        self._editor.painted.disconnect(self._draw)

    def initialize(self):
        self.__positions = [79]
        self.color.background = 'white'

    def _draw(self, event):
        painter = QPainter(self._editor.viewport())
        painter.setPen(self.color.background)
        metrics = QFontMetricsF(self._editor.document().defaultFont())
        doc_margin = self._editor.document().documentMargin()
        offset = self._editor.contentOffset().x() + doc_margin
        rect = self._editor.viewport().rect()
        for pos in self.__positions:
            if pos <= 0 or pos >= rect.width():
                continue
            x = round(metrics.width(' ') * pos) + offset
            painter.drawLine(x, rect.top(), x, rect.bottom())
