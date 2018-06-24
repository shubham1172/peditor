"""
editor.py: editor functions
"""
from utils import getch, ctrl_key, pexit, pprint, get_terminal_size


def init():
    global _rows, _cols
    _rows, _cols = get_terminal_size()


def _raw_read():
    c = getch()
    return c


def read_key():
    c = _raw_read()
    if c == ctrl_key('q'):
        pexit()


def refresh_screen():
    pprint("\x1b[?25l")         # hide cursor
    pprint("\x1b[2J")           # clear entire screen
    pprint("\x1b[H")            # reposition cursor
    draw_rows()
    pprint("\x1b[H")            # reposition cursor
    pprint("\x1b[?25h")         # show cursor


def draw_rows():
    global _rows, _cols
    welcome_message = "peditor -- welcome"
    for row in range(_rows):
        pprint("~")
        if row == _rows//3:
            pad_string = " "*((_cols - len(welcome_message)) // 2)
            pprint(pad_string, welcome_message)
        if row < (_rows - 1):
            pprint("\n")
