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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu

from PyQt5.QtGui import QPainter

from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import QPoint

from ninja_ide.gui.editor.features import Feature


class SideBarWidget(Feature, QWidget):

    sidebarContextMenuRequested = Signal(int, QMenu)

    def __init__(self):
        Feature.__init__(self)
        QWidget.__init__(self)
        self.object_name = self.__class__.__name__
        self.order = -1

    def register(self, editor):
        super().register(editor)
        self.setParent(editor)

    def unregister(self):
        super().unregister()
        self.setParent(None)

    def contextMenuEvent(self, event):
        cursor = self._neditor.cursorForPosition(QPoint(0, event.pos().y()))
        menu = QMenu(self)
        self.sidebarContextMenuRequested.emit(cursor.blockNumber(), menu)
        if not menu.isEmpty():
            menu.exec_(event.globalPos())
        menu.deleteLater()
        event.accept()

    def paintEvent(self, event):
        if self.isVisible():
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.color.background)

    def setVisible(self, value):
        """Show/Hide the widget"""
        QWidget.setVisible(self, value)
        # self._editor.side_widgets.update_viewport()


from ninja_ide.gui.editor.side_area.manager import SideWidgetManager  # noqa
from ninja_ide.gui.editor.side_area.line_number_widget import LineNumberWidget  # noqa
from ninja_ide.gui.editor.side_area.text_change_widget import TextChangeWidget  # noqa
from ninja_ide.gui.editor.side_area.code_folding import CodeFoldingWidget  # noqa

__all__ = [
    'SideBarWidget',
    'SideWidgetManager',
    'LineNumberWidget',
    'TextChangeWidget',
    'CodeFoldingWidget'
]
