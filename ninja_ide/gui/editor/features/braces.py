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

from PySide2.QtCore import Qt
from PySide2.QtGui import QTextCursor
from ninja_ide.gui.editor.features import Feature


class AutocompleteBraces(Feature):
    """Automatically complete braces"""

    OPENED_BRACES = "[{("
    CLOSED_BRACES = "]})"
    ALL_BRACES = {
        "(": ")",
        "[": "]",
        "{": "}"
    }

    def on_enabled(self):
        self._editor.postKeyPressed.connect(self._on_post_key_pressed)
        self._editor.keyPressed.connect(self._on_key_pressed)

    def on_disabled(self):
        self._editor.postKeyPressed.disconnect(self._on_post_key_pressed)
        self._editor.keyPressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        right = self._editor.get_right_character()
        current_text = event.text()
        if current_text in self.CLOSED_BRACES and right == current_text:
            # Move cursor to right if same symbol is typing
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.MoveAnchor)
            self._editor.setTextCursor(cursor)
            event.accept()
        elif event.key() == Qt.Key_Backspace:
            # Remove automatically closed symbol if opened symbol is removed
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            to_remove = cursor.selectedText()
            if to_remove in self.ALL_BRACES.keys():  # Opened braces
                complementary = self.ALL_BRACES.get(to_remove)
                if complementary is not None and complementary == right:
                    cursor.movePosition(
                        QTextCursor.Right, QTextCursor.KeepAnchor)
                    cursor.insertText('')
                    event.accept()

    def _on_post_key_pressed(self, event):
        # Insert complementary symbol
        char = event.text()
        if not char:
            return
        right = self._editor.get_right_character()
        cursor = self._editor.textCursor()
        if char in self.OPENED_BRACES:
            to_insert = self.ALL_BRACES[char]
            if not right or right in self.CLOSED_BRACES or right.isspace():
                cursor.insertText(to_insert)
                cursor.movePosition(QTextCursor.PreviousCharacter)
                self._editor.setTextCursor(cursor)
