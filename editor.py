"""
editor.py: editor functions
"""
import time
from keys import EditorKeys
from utils import getch, ctrl_key, pexit, pprint, get_terminal_size, \
    convert_rows_to_string, convert_string_to_rows


def init():
    global _rows, _cols, cx, cy, \
        fileLoaded, fileRows, roff, coff, \
        file_name, status_message, status_message_time, \
        dirty, quit_times
    cx, cy = 0, 0   # curr cursor location
    _rows, _cols = get_terminal_size()
    _rows -= 2      # status and message bar
    fileLoaded = False
    fileRows = []
    roff = 0        # row coefficient
    coff = 0        # col coefficient
    file_name = None
    status_message = ""
    status_message_time = 0
    dirty = False   # indicate that file is modified
    quit_times = 3  # number of times to press quit for closing dirty files


""" input """


def raw_read():
    c = getch()
    if c == chr(127):
        return EditorKeys.BACKSPACE
    elif c == '\t':
        return EditorKeys.TAB_KEY
    elif c == '\x1b':         # ESC character
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
    global _rows, _cols, cx, cy, roff, fileRows, dirty, quit_times
    c = raw_read()
    if c == ctrl_key('q'):
        if dirty and quit_times > 0:
            set_status_message("WARNING: File has unsaved changes. "
                               "Press CTRL-q %d more time(s) to quit" % quit_times)
            quit_times -= 1
        else:
            pexit()
    elif c == ctrl_key('s'):
        save_file()
    elif c in ('\r', '\n'):
        # TODO
        pass
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
        if cy < len(fileRows):
            cx = len(fileRows[cy])
    elif c in (EditorKeys.BACKSPACE, EditorKeys.DEL_KEY, ctrl_key('h')):
        if c == EditorKeys.DEL_KEY:
            move_cursor(EditorKeys.ARROW_RIGHT)
        delete_char()
    elif c in (ctrl_key('l'), '\x1b'):
        # TODO
        pass
    elif c == EditorKeys.TAB_KEY:
        for _ in range(4):
            insert_char(' ')
    else:
        insert_char(c)


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
    draw_status_bar()
    draw_message_bar()
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
        pprint("\n")


def draw_status_bar():
    global file_name, _cols, fileRows, cy, dirty
    pprint("\x1b[7m")  # invert colors
    s = file_name if file_name else "[No Name]"
    left = "%s - %d lines %s" % (s[0:20],
                                 len(fileRows),
                                 "(modified)" if dirty else "")
    right = "%d/%d" % (cy + 1, len(fileRows))
    pad = " "*(_cols-len(left)-len(right))
    display_string = left + pad + right
    pprint(display_string[0:_cols])
    pprint("\x1b[m")   # restore colors
    pprint("\n")


def set_status_message(*args):
    global status_message, status_message_time
    status_message = " ".join(args)
    status_message_time = time.time()


def draw_message_bar():
    global status_message, status_message_time, _cols
    pprint("\x1b[K")    # clear the line
    if (time.time() - status_message_time) < 5:
        pprint(status_message[0:_cols])


def insert_char_at_row(row, at, c):
    global fileRows, dirty
    if at < 0 or at > len(fileRows[row]):
        at = len(fileRows[row])
    fileRows[row] = fileRows[row][0:at] + c + fileRows[row][at:]
    dirty = True


def insert_char(c):
    global cx, cy, fileRows
    if cy == len(fileRows):
        fileRows.append("")
    insert_char_at_row(cy, cx, c)
    cx += 1


def delete_char_at_row(row, at):
    global fileRows, dirty
    if at < 0 or at >= len(fileRows[row]):
        return
    fileRows[row] = fileRows[row][0:at] + fileRows[row][at+1:]
    dirty = True


def delete_char():
    global cx, cy, fileRows
    if cy == len(fileRows):
        return
    if cx > 0:
        delete_char_at_row(cy, cx - 1)
        cx -= 1


""" cursor """


def move_cursor(c):
    global cx, cy, _rows, _cols, roff, coff, fileRows

    row = None if cy >= len(fileRows) else fileRows[cy]

    if c == EditorKeys.ARROW_UP:
        if cy != 0:
            cy -= 1
    elif c == EditorKeys.ARROW_DOWN:
        if cy < len(fileRows) - 1:
            cy += 1
    elif c == EditorKeys.ARROW_LEFT:
        if cx != 0:
            cx -= 1
        elif cy > 0:
            cy -= 1
            cx = len(fileRows[cy])
    elif c == EditorKeys.ARROW_RIGHT:
        if row and cx < len(fileRows[cy]):
            cx += 1
        elif row and cy < len(fileRows):
            cy += 1
            cx = 0

    row = "" if cy >= len(fileRows) else fileRows[cy]

    if cx > len(row):
        cx = len(row)


def update_cursor():
    global cx, cy, roff, coff
    pprint("\x1b[%d;%dH" % (cy - roff + 1, cx - coff + 1))


""" file handling """


def load_file(filename):
    global fileLoaded, fileRows, file_name, dirty
    try:
        with open(filename, 'r') as file:
            fileRows = convert_string_to_rows(file.read())
        fileLoaded = True
        file_name = filename
    except IOException:
        pexit("error opening %s\n" % filename)
    dirty = False


def save_file():
    global fileRows, file_name, dirty
    if not file_name:
        return
    try:
        with open(file_name, 'r+') as file:
            text = convert_rows_to_string(fileRows)
            file.write(text)
            set_status_message("%d bytes written to disk." % len(text))
    except IOException as e:
        set_status_message("error writing to %s\n - %s" % (file_name, str(e)))
    dirty = False
