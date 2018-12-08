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

from PySide2.QtGui import QTextCursor
from PySide2.QtCore import Qt
from ninja_ide.gui.editor.features import Feature


class Quotes(Feature):

    QUOTES = {
        Qt.Key_QuoteDbl: '"',
        Qt.Key_Apostrophe: "'"
    }

    def on_enabled(self):
        self._editor.keyPressed.connect(self._on_key_pressed)

    def on_disabled(self):
        self._editor.keyPressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        if event.isAccepted():
            return
        key = event.key()
        if key in self.QUOTES.keys():
            self._autocomplete_quotes(key)
            event.accept()

    def get_left_chars(self, nchars=1):
        cursor = self._editor.textCursor()
        chars = None
        for i in range(nchars):
            if not cursor.atBlockStart():
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                chars = cursor.selectedText()
        return chars

    def _autocomplete_quotes(self, key):
        char = self.QUOTES[key]
        cursor = self._editor.textCursor()
        two = self.get_left_chars(2)
        three = self.get_left_chars(3)
        if self._editor.has_selection():
            text = self._editor.selected_text()
            cursor.insertText("{0}{1}{0}".format(char, text))
            # Keep selection
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor)
            cursor.movePosition(
                QTextCursor.Left, QTextCursor.KeepAnchor, len(text))
        elif self._editor.get_right_character() == char:
            cursor.movePosition(
                QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            cursor.clearSelection()
        elif three == char * 3:
            cursor.insertText(char * 3)
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 3)
        elif two == char * 2:
            cursor.insertText(char)
        else:
            cursor.insertText(char * 2)
            cursor.movePosition(QTextCursor.PreviousCharacter)
        self._editor.setTextCursor(cursor)
