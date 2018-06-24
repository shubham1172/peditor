"""
editor.py: editor functions
"""
from keys import EditorKeys
from utils import getch, ctrl_key, pexit, pprint, get_terminal_size


def init():
    global _rows, _cols, cx, cy, \
        fileLoaded, fileRows, roff, coff
    cx, cy = 0, 0   # curr cursor location
    _rows, _cols = get_terminal_size()
    fileLoaded = False
    fileRows = []
    roff = 0
    coff = 0


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
    global _rows, _cols, cx, cy, roff, fileRows
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
        if c == EditorKeys.PAGE_UP:
            cy = roff

        times = _rows
        while times > 0:
            move_cursor(EditorKeys.ARROW_UP if c == EditorKeys.PAGE_UP
                        else EditorKeys.ARROW_DOWN)
            times -= 1
    elif c == EditorKeys.HOME_KEY:
        cx = 0
    elif c == EditorKeys.END_KEY:
        cx = len(fileRows[cy - roff])


""" screen """


def scroll_editor():
    global cy, roff, _rows, \
            cx, coff, _cols
    if cy < roff:
        roff = cy
    if cy >= (roff + _rows):
        roff = cy - _rows + 1
    if cx < coff:
        coff = cx
    if cx >= (coff + _cols):
        coff = cx - _cols + 1


def refresh_screen():
    scroll_editor()
    pprint("\x1b[?25l")         # hide cursor
    pprint("\x1b[2J")           # clear entire screen
    pprint("\x1b[H")            # reposition cursor
    draw_rows()
    update_cursor()
    pprint("\x1b[?25h")         # show cursor


def draw_rows():
    global _rows, _cols, fileLoaded, fileRows, roff, coff
    welcome_message = "peditor -- welcome"
    for row in range(_rows):
        file_row = row + roff
        if not fileLoaded:
            pprint("~ ")
        if file_row < len(fileRows):
            pprint(fileRows[file_row][coff:coff+_cols])
        if row == _rows//3 and not fileLoaded:
            pad_string = " "*((_cols - len(welcome_message)) // 2)
            pprint(pad_string, welcome_message)
        if row < (_rows - 1):
            pprint("\n")


""" cursor """


def move_cursor(c):
    global cx, cy, _rows, _cols, roff, coff, fileRows
    if c == EditorKeys.ARROW_UP:
        if cy != 0:
            cy -= 1
    elif c == EditorKeys.ARROW_DOWN:
        if cy < len(fileRows):
            cy += 1
    elif c == EditorKeys.ARROW_LEFT:
        if cx != 0:
            cx -= 1
        elif cy > 0:
            cy -= 1
            cx = len(fileRows[cy - roff])
    elif c == EditorKeys.ARROW_RIGHT:
        if (cy - roff) < len(fileRows) and cx < len(fileRows[cy - roff]):
            cx += 1
        elif (cy - roff) < len(fileRows) and cy < len(fileRows):
            cy += 1
            cx = 0

    if (cy - roff) < len(fileRows) and cx > len(fileRows[cy - roff]):
        cx = len(fileRows[cy - roff])


def update_cursor():
    global cx, cy, roff, coff
    pprint("\x1b[%d;%dH" % (cy - roff + 1, cx - coff + 1))


""" file handling """


def load_file(filename):
    global fileLoaded, fileRows
    try:
        with open(filename, 'r') as file:
            fileRows = file.read().split('\n')
        fileLoaded = True
    except:
        pexit("error opening %s\n" % filename)
