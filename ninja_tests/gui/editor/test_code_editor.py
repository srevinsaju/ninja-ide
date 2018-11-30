import pytest

from ninja_ide.gui.editor.base import CodeEditor


@pytest.fixture
def code_editor():
    editor = CodeEditor()
    editor.text = "NINJA-IDE is not just another IDE"
    return editor


def test_find_match(code_editor):
    assert code_editor.find_match('IDE') is True
    _, col = code_editor.cursor_position
    assert col == 9


def test_find_match_cs(code_editor):
    assert code_editor.find_match('JUST', True) is False


def test_find_match_wo(code_editor):
    assert code_editor.find_match('ju', whole_word=True) is False


def test_replace_match(code_editor):
    code_editor.find_match('just')
    code_editor.replace_match(
        word_old='just',
        word_new='JUST'
    )
    assert code_editor.text == 'NINJA-IDE is not JUST another IDE'


def test_replace_all(code_editor):
    code_editor.replace_all(
        word_old='IDE',
        word_new='Integrated Development Environment'
    )
    assert code_editor.text == (
        'NINJA-Integrated Development Environment is not just another '
        'Integrated Development Environment')


@pytest.mark.parametrize(
    'text, line, col, center, expected',
    [
        ('NINJA-IDE\nis\nnot\nJUST\nanother\nIDE', 1, 3, False, (1, 2)),
        ('NINJA-IDE\nis\nnot\nJUST\nanother\nIDE', 23, 1, False, (0, 0)),
    ]
)
def test_go_to_line(code_editor, text, line, col, center, expected):
    code_editor.text = text
    code_editor.go_to_line(line, col, center)
    assert code_editor.cursor_position == expected


def test_zoom(code_editor):
    font = code_editor.document().defaultFont()
    assert font.pointSize() == 12  # default
    for i in range(4):
        code_editor.zoom(delta=1)
    font = code_editor.document().defaultFont()
    assert font.pointSize() == 16
    for i in range(6):
        code_editor.zoom(delta=-1)
    font = code_editor.document().defaultFont()
    assert font.pointSize() == 10


@pytest.mark.parametrize(
    'text, expected',
    [
        ('def foo():\n    pass   ', 'def foo():\n    pass'),
        ('def foo(): \n    pass   ', 'def foo():\n    pass'),
    ]
)
def test_remove_trailing_spaces(code_editor, text, expected):
    code_editor.text = text
    code_editor.remove_trailing_spaces()
    assert code_editor.text == expected


def test_insert_block_at_end(code_editor):
    text = code_editor.text
    code_editor.insert_block_at_end()
    assert code_editor.text == text + '\n'
    code_editor.insert_block_at_end()
    assert code_editor.text == text + '\n'
