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

from PySide2.QtGui import QColor
from PySide2.QtGui import QPainter
from PySide2.QtGui import QPen
from PySide2.QtGui import QFontMetrics
from PySide2.QtGui import QFontMetricsF

from PySide2.QtCore import Qt
from PySide2.QtCore import QSize

from ninja_ide.gui.editor.side_area import SideBarWidget
from ninja_ide import resources


class LineNumberWidget(SideBarWidget):
    """
    Line number area Widget
    """
    LEFT_MARGIN = 5
    RIGHT_MARGIN = 3

    def on_enabled(self):
        self._editor.zoomChanged.connect(
            self._editor.side_widgets.update_viewport)

    def on_disabled(self):
        self._editor.zoomChanged.disconnect(
            self._editor.side_widgets.update_viewport)

    def initialize(self):
        self.color.background = resources.COLOR_SCHEME.get('editor.line_number.background')
        self.color.foreground = resources.COLOR_SCHEME.get('editor.line_number.foreground')
        # self._color_unselected = QColor(
        #     resources.COLOR_SCHEME.get('editor.sidebar.foreground'))
        self._color_selected = QColor(
            resources.COLOR_SCHEME.get("editor.line"))

    def sizeHint(self):
        return QSize(self.__calculate_width(), 0)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        width = self.width() - self.RIGHT_MARGIN - self.LEFT_MARGIN
        height = QFontMetricsF(self._editor.document().defaultFont()).height()
        font = self._editor.document().defaultFont()
        font_bold = self._editor.document().defaultFont()
        font_bold.setBold(True)
        pen = QPen(self.color.foreground)
        painter.setPen(pen)
        painter.setFont(font)
        sel_start, sel_end = self._editor.selection_range()
        has_sel = sel_start != sel_end
        current_line, _ = self._editor.cursor_position
        # Draw visible blocks
        for top, line, block in self._editor.visible_blocks:
            # Set bold to current line and selected lines
            if ((has_sel and sel_start <= line <= sel_end) or
                    (not has_sel and current_line == line)):
                painter.setFont(font_bold)
            else:
                painter.setPen(pen)
                painter.setFont(font)
            painter.drawText(self.LEFT_MARGIN, top, width, height,
                             Qt.AlignRight, str(line + 1))

    def __calculate_width(self):
        digits = len(str(max(1, self._editor.blockCount())))
        fmetrics_width = QFontMetrics(
            self._editor.document().defaultFont()).width('9')

        return self.LEFT_MARGIN + fmetrics_width * digits + self.RIGHT_MARGIN

    def mousePressEvent(self, event):
        self.__selecting = True
        self.__selection_start_pos = event.pos().y()
        start = end = self._editor.line_from_position(
            self.__selection_start_pos)
        self.__selection_start_line = start
        self._editor.select_lines(start, end)

    def mouseMoveEvent(self, event):
        if self.__selecting:
            end_pos = event.pos().y()
            end_line = self._editor.line_from_position(end_pos)
            if end_line == -1:
                return
            self._editor.select_lines(self.__selection_start_line, end_line)

    def wheelEvent(self, event):
        self._editor.wheelEvent(event)
