"""
editor.py: editor functions
"""
from keys import EditorKeys
from utils import getch, ctrl_key, pexit, pprint, get_terminal_size


def init():
    global _rows, _cols, cx, cy
    cx, cy = 0, 0   # curr cursor location
    _rows, _cols = get_terminal_size()


""" input """


def raw_read():
    c = getch()
    if c == '\x1b':         # ESC character
        c1 = getch()
        c2 = getch()
        if (not c1) or (not c2):
            return c
        if c1 == '[':
            if '0' <= c2 <= '9':
                c3 = getch()
                if not c3:
                    return c
                if c3 == '~':
                    if c2 == '1':
                        return EditorKeys.HOME_KEY
                    elif c2 == '3':
                        return EditorKeys.DEL_KEY
                    elif c2 == '4':
                        return EditorKeys.END_KEY
                    elif c2 == '5':
                        return EditorKeys.PAGE_UP
                    elif c2 == '6':
                        return EditorKeys.PAGE_DOWN
                    elif c2 == '7':
                        return EditorKeys.HOME_KEY
                    elif c2 == '8':
                        return EditorKeys.END_KEY
            else:
                if c2 == 'A':
                    return EditorKeys.ARROW_UP
                elif c2 == 'B':
                    return EditorKeys.ARROW_DOWN
                elif c2 == 'C':
                    return EditorKeys.ARROW_RIGHT
                elif c2 == 'D':
                    return EditorKeys.ARROW_LEFT
                elif c2 == 'H':
                    return EditorKeys.HOME_KEY
                elif c2 == 'F':
                    return EditorKeys.END_KEY
        elif c1 == 'O':
            if c2 == 'H':
                return EditorKeys.HOME_KEY
            elif c2 == 'F':
                return EditorKeys.END_KEY
    return c


def read_key():
    global _rows, _cols, cx, cy
    c = raw_read()
    if c == ctrl_key('q'):
        pexit()
    elif c in (EditorKeys.ARROW_UP,
               EditorKeys.ARROW_LEFT,
               EditorKeys.ARROW_RIGHT,
               EditorKeys.ARROW_DOWN):
        move_cursor(c)
    elif c in (EditorKeys.PAGE_UP,
               EditorKeys.PAGE_DOWN):
        times = _rows
        while times > 0:
            move_cursor(EditorKeys.ARROW_UP if c == EditorKeys.PAGE_UP
                        else EditorKeys.ARROW_DOWN)
            times -= 1
    elif c == EditorKeys.HOME_KEY:
        cx = 0
    elif c == EditorKeys.END_KEY:
        cx = _cols - 1


""" screen """


def refresh_screen():
    pprint("\x1b[?25l")         # hide cursor
    pprint("\x1b[2J")           # clear entire screen
    pprint("\x1b[H")            # reposition cursor
    draw_rows()
    update_cursor()
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


""" cursor """


def move_cursor(c):
    global cx, cy, _rows, _cols
    if c == EditorKeys.ARROW_UP:
        if cy != 0:
            cy -= 1
    elif c == EditorKeys.ARROW_DOWN:
        if cy != (_rows - 1):
            cy += 1
    elif c == EditorKeys.ARROW_LEFT:
        if cx != 0:
            cx -= 1
    elif c == EditorKeys.ARROW_RIGHT:
        if cx != (_cols - 1):
            cx += 1


def update_cursor():
    global cx, cy
    pprint("\x1b[%d;%dH" % (cy+1, cx+1))
