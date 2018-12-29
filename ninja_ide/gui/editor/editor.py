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
import re
import sre_constants

from PySide2.QtWidgets import QToolTip

from PySide2.QtGui import QTextCursor
from PySide2.QtGui import QKeySequence
from PySide2.QtGui import QPaintEvent
from PySide2.QtGui import QPainter
from PySide2.QtGui import QKeyEvent
from PySide2.QtGui import QFontMetrics
from PySide2.QtGui import QColor

from PySide2.QtCore import Signal
from PySide2.QtCore import QEvent
from PySide2.QtCore import Qt
from PySide2.QtCore import QPoint
from PySide2.QtCore import QTimer

from ninja_ide import resources
# from ninja_ide.tools import utils
from ninja_ide.gui.editor.base import CodeEditor
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import scrollbar
from ninja_ide.gui.editor import indenter

from ninja_ide.gui.editor.extra_selection import ExtraSelection
from ninja_ide.gui.editor import features
from ninja_ide.gui.editor import side_area

_MAX_CHECKER_SELECTIONS = 150  # For good performance


class NEditor(CodeEditor):

    positionChanged = Signal(int, int)
    currentLineChanged = Signal(int)
    painted = Signal(QPaintEvent)
    keyPressed = Signal(QKeyEvent)
    postKeyPressed = Signal(QKeyEvent)

    def __init__(self, neditable=None):
        super().__init__()
        self.setMouseTracking(True)
        self.setCursorWidth(2)
        self._neditable = neditable
        self.__encoding = None
        self._last_line_position = 0
        self._highlighter = None
        self._indenter = indenter.load_indenter(self, neditable.language())
        # For highlight search results
        self._highlight_results_timer = QTimer(self)
        self._highlight_results_timer.setSingleShot(True)
        self._highlight_results_timer.timeout.connect(self.viewport().update)
        self._search_expression = None

        # Extra selection manager
        self._extra_selections = ExtraSelectionManager(self)
        # Feature manager
        self._features = features.FeatureManager(self)
        # Install features
        self._features.install(features.CurrentLine)
        self._features.install(features.AutocompleteBraces)
        self._features.install(features.Ruler)
        self._features.install(features.SymbolHighlighter)
        self._features.install(features.Quotes)

        # Side widgets manager
        self._side_widgets = side_area.SideWidgetManager(self)
        # Custom scrollbar
        self._scrollbar = scrollbar.NScrollBar(self)
        self.setVerticalScrollBar(self._scrollbar)
        # Set the editor after initialization
        if self._neditable is not None:
            if self._neditable.editor:
                self.setDocument(self._neditable.document)
            else:
                self._neditable.set_editor(self)
            self._neditable.checkersUpdated.connect(self._highlight_checkers)
        # Install side widgets
        self._side_widgets.add(side_area.TextChangeWidget)
        self._side_widgets.add(side_area.LineNumberWidget)
        self._side_widgets.add(side_area.CodeFoldingWidget)

        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.currentLineChanged.connect(self.viewport().update)

    @property
    def nfile(self):
        return self._neditable.nfile

    @property
    def neditable(self):
        return self._neditable

    @property
    def file_path(self):
        return self._neditable.file_path

    @property
    def is_modified(self):
        return self.document().isModified()

    @property
    def encoding(self):
        if self.__encoding is not None:
            return self.__encoding
        return "utf-8"

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    @property
    def extra_selections(self):
        return self._extra_selections

    @property
    def features(self):
        return self._features

    @property
    def side_widgets(self):
        return self._side_widgets

    def _highlight_checkers(self, editable):
        """Highlight errors, warnings..."""
        self._extra_selections.remove('checkers')
        self._scrollbar.remove_marker('checkers')
        checkers = editable.sorted_checkers
        selections = []
        append = selections.append  # Reduce name look-ups for better speed
        for items in checkers:
            checker, color, _ = items
            lines = list(checker.checks.keys())
            lines.sort()
            for line in lines[:_MAX_CHECKER_SELECTIONS]:
                cursor = self.textCursor()
                self._scrollbar.add_marker('checkers', line, color)
                ms = checker.checks[line]
                for (col_start, col_end), _, _ in ms:
                    selection = ExtraSelection(
                        cursor,
                        start_line=line,
                        col_start=col_start,
                        col_end=col_end
                    )
                    selection.set_underline(color)
                    append(selection)
        self._extra_selections['checkers'] = selections

    def _on_cursor_position_changed(self):
        line, col = self.cursor_position
        self.positionChanged.emit(line, col)
        if line != self._last_line_position:
            self._last_line_position = line
            self.currentLineChanged.emit(line)
        # Update marker for scrollbar
        self.update_current_line_in_scrollbar(line)

    def update_current_line_in_scrollbar(self, current_line):
        """Update current line highlight in scrollbar"""

        self._scrollbar.remove_marker('current_line')
        if self._scrollbar.maximum() > 0:
            self._scrollbar.add_marker(
                "current_line", current_line, "white", priority=2)

    def register_syntax_for(self, language='python'):
        syntax = highlighter.build_highlighter(language)
        if syntax is not None:
            self._highlighter = highlighter.SyntaxHighlighter(
                self.document(),
                syntax.partition_scanner,
                syntax.scanners,
                syntax.context
            )

    def keyPressEvent(self, event):
        if self.isReadOnly():
            return
        event.ignore()
        # Emit a signal so that plugins can do their thing
        self.keyPressed.emit(event)

        if event.matches(QKeySequence.InsertParagraphSeparator):
            cursor = self.textCursor()
            self._indenter.indent_block(cursor)
            event.accept()
        if event.key() == Qt.Key_Home:
            self.__manage_key_home(event)
        elif event.key() == Qt.Key_Backspace:
            if not event.isAccepted():
                if self.__smart_backspace():
                    event.accept()
        if not event.isAccepted():
            super().keyPressEvent(event)

        self.postKeyPressed.emit(event)

    def __smart_backspace(self):
        accepted = False
        cursor = self.textCursor()
        text_before_cursor = self.text_before_cursor(cursor)
        text = cursor.block().text()
        indentation = self._indenter.text()
        space_at_start_len = len(text) - len(text.lstrip())
        column_number = cursor.positionInBlock()
        if text_before_cursor.endswith(indentation) and \
                space_at_start_len == column_number and \
                not cursor.hasSelection():
            to_remove = len(text_before_cursor) % len(indentation)
            if to_remove == 0:
                to_remove = len(indentation)
            cursor.setPosition(cursor.position() - to_remove,
                               QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            accepted = True
        return accepted

    def __manage_key_home(self, event):
        """Performs home key action"""
        cursor = self.textCursor()
        indent = self.line_indent()
        # For selection
        move = QTextCursor.MoveAnchor
        if event.modifiers() == Qt.ShiftModifier:
            move = QTextCursor.KeepAnchor
        # Operation
        if cursor.positionInBlock() == indent:
            cursor.movePosition(QTextCursor.StartOfBlock, move)
        elif cursor.atBlockStart():
            cursor.setPosition(cursor.block().position() + indent, move)
        elif cursor.positionInBlock() > indent:
            cursor.movePosition(QTextCursor.StartOfLine, move)
            cursor.setPosition(cursor.block().position() + indent, move)
        self.setTextCursor(cursor)
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_scrollbar_ranges()
        self._side_widgets.resize()

    def paintEvent(self, event):
        super().paintEvent(event)
        # Emit a singal so that plugins can do their thing
        self.painted.emit(event)
        self._paint_search_results()

    def showEvent(self, event):
        super().showEvent(event)
        self._side_widgets.update_viewport()

    def viewportEvent(self, event):
        if event.type() == QEvent.ToolTip:
            pos = event.pos()
            tc = self.cursorForPosition(pos)
            block = tc.block()
            line = block.layout().lineForTextPosition(tc.positionInBlock())
            if line.isValid():
                if pos.x() <= self.blockBoundingRect(block).left() + \
                        line.naturalTextRect().right():
                    column = tc.positionInBlock()
                    line = self.cursorForPosition(pos).blockNumber()
                    checkers = self._neditable.sorted_checkers
                    for items in checkers:
                        checker, _, _ = items
                        messages_for_line = checker.message(line)
                        if messages_for_line is not None:
                            for (start, end), message, content in \
                                    messages_for_line:
                                if column >= start and column <= end:
                                    QToolTip.showText(
                                        self.mapToGlobal(pos), message, self)
                    return True
                QToolTip.hideText()
        return super().viewportEvent(event)

    def adjust_scrollbar_ranges(self):
        line_spacing = QFontMetrics(self.font()).lineSpacing()
        if line_spacing == 0:
            return
        offset = self.contentOffset().y()
        self._scrollbar.set_visible_range(
            (self.viewport().rect().height() - offset) / line_spacing)
        self._scrollbar.set_range_offset(offset / line_spacing)

    def link(self, clone):
        clone._scrollbar.link(self._scrollbar)

    def highlight_search_results(self, text, cs=False, wo=False):
        if self._search_expression == text:
            return
        self._search_expression = text
        self._highlight_results_timer.start(50)

    def _get_search_results(self, target):
        cursor = self.cursorForPosition(QPoint(0, 0))
        doc = self.document()
        for _ in range(200):  # FIXME:
            cursor = doc.find(
                self._search_expression, cursor)
            if cursor is None or cursor.isNull():
                # No more matches found
                break
            end_rect = self.cursorRect(cursor)
            if end_rect.bottom() > self.height():
                # Don't highlight the rest of not visible document
                break
            cursor.setPosition(min(cursor.position(), cursor.anchor()))
            start_rect = self.cursorRect(cursor)
            width = end_rect.left() - start_rect.left()
            yield start_rect, width
            cursor.movePosition(cursor.EndOfWord)

    def clear_search_results(self):
        self._search_expression = None
        self.viewport().update()

    def _paint_search_results(self):
        painter = QPainter(self.viewport())
        color = QColor(resources.COLOR_SCHEME.get('editor.search.result'))
        painter.setPen(color)
        color.setAlpha(50)
        painter.setBrush(color)

        for rect, width in self._get_search_results(self._search_expression):
            painter.drawRoundedRect(
                rect.left(), rect.top(),
                width, rect.height(), 2, 2
            )
    # def highlight_found_results(self, text, cs=False, wo=False):
    #     """Highlight all found results from find/replace widget"""

    #     if self._search_expression == text:
    #         return 0, 0
    #     self._search_expression = text
    #     self._highlight_results_timer.start(100)
        # if self._search_expression == text:
        #     return
        # self._search_expression = text
        # self._highlight_results_timer.start(100)
        # index, results = self._get_find_index_results(text, cs=cs, wo=wo)
        # selections = []
        # append = selections.append
        # color = resources.COLOR_SCHEME.get("editor.search.result")
        # for start, end in results:
        #     selection = ExtraSelection(
        #         self.textCursor(), start_pos=start, end_pos=end)
        #     selection.set_background(color)
        #     selection.set_foreground(utils.get_inverted_color(color))
        #     append(selection)
        #     line = selection.cursor.blockNumber()
        #     self._scrollbar.add_marker("find", line, color)
        # self._extra_selections["find"] = selections

        # return index, len(results)
        # return 0, 0

    def _get_find_index_results(self, expr, cs, wo):

        text = self.text
        current_index = 0

        if not cs:
            text = text.lower()
            expr = expr.lower()

        expr = re.escape(expr)
        if wo:
            expr = r"\b" + re.escape(expr) + r"\b"

        def find_all_iter(string, sub):
            try:
                reobj = re.compile(sub)
            except sre_constants.error:
                return
            for match in reobj.finditer(string):
                yield match.span()

        matches = list(find_all_iter(text, expr))

        if len(matches) > 0:
            position = self.textCursor().position()
            current_index = sum(1 for _ in re.finditer(expr, text[:position]))
        return current_index, matches


class ExtraSelectionManager:
    """QTextEdit.ExtraSelection manager"""

    def __init__(self, neditor: NEditor):
        self._neditor = neditor
        self._selections = {}

    def __len__(self):
        return len(self._selections)

    def __iter__(self):
        return iter(self._selections)

    def __setitem__(self, kind: str, selection):
        if not isinstance(selection, list):
            selection = [selection]
        self._selections[kind] = selection
        self.update()

    def __getitem__(self, kind):
        return self._selections.get(kind, [])

    def update(self):
        selections = []
        for kind, selection in self._selections.items():
            selections.extend(selection)
        selections = sorted(selections, key=lambda sel: sel.order)
        self._neditor.setExtraSelections(selections)

    def remove(self, kind):
        """Removes a extra selection from the editor"""
        if kind in self._selections:
            self._selections[kind].clear()
            self.update()

    def clear(self):
        """Remove all extra selections from the editor"""
        for kind in self:
            self.remove(kind)


def create_editor(neditable=None):
    neditor = NEditor(neditable)
    language = neditable.language()
    if language is None:
        # For python files without the extension
        # FIXME: Move to another module
        # FIXME: Generalize it?
        for line in neditor.text.splitlines():
            if not line.strip():
                continue
            if line.startswith("#!"):
                shebang = line[2:]
                if "python" in shebang:
                    language = "python"
            else:
                break
    neditor.register_syntax_for(language)
    return neditor
