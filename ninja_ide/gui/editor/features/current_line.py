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
from ninja_ide.gui.editor.extra_selection import ExtraSelection

_LINE_MODE = 'line'
_FULL_MODE = 'full'


class CurrentLine(Feature):

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        self._mode = mode
        self.update()

    def initialize(self):
        self._mode = _LINE_MODE
        self.color.background = 'white'
        self._color = self.color.background

    def on_enabled(self):
        if self._mode == _LINE_MODE:
            self._editor.painted.connect(self._paint_line_mode)
        else:
            self._editor.currentLineChanged.connect(self._highlight_full_mode)

    def on_disabled(self):
        if self._mode == _LINE_MODE:
            self._editor.painted.disconnect(self._paint_line_mode)
        else:
            self._editor.currentLineChanged.disconnect(
                self._highlight_full_mode)

    def _paint_line_mode(self, event):
        block = self._editor.textCursor().block()
        layout = block.layout()
        line_count = layout.lineCount()
        line = layout.lineAt(line_count - 1)
        if line_count < 1:
            return
        font_height = QFontMetricsF(
            self._editor.document().defaultFont()).height()
        offset = self._editor.contentOffset()
        top = self._editor.blockBoundingGeometry(block).translated(
            offset).top()
        line_rect = line.naturalTextRect().translated(offset.x(), top)
        painter = QPainter(self._editor.viewport())
        painter.setPen(self._color)
        painter.drawLine(
            line_rect.x(),
            line_rect.y() + font_height,
            self._editor.width(),
            line_rect.y() + font_height
        )

    def _highlight_full_mode(self):
        selection = ExtraSelection(self._editor.textCursor())
        selection.set_full_width()
        selection.set_background(self._color)
        self._editor.extra_selections['current_line'] = selection
