"""
editor.py: editor functions
"""
import time
from keys import EditorKeys
from utils import getch, is_ctrl, ctrl_key, pexit, pprint, get_terminal_size, \
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


def reset_dirty():
    global dirty, quit_times
    dirty = False
    quit_times = 3


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
        insert_new_line()
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
    global _rows, _cols, fileLoaded, fileRows, roff, coff, dirty
    welcome_message = "peditor -- welcome"
    for row in range(_rows):
        file_row = row + roff
        if file_row < len(fileRows):
            pprint(fileRows[file_row][coff:coff+_cols])
        if row == _rows//3 and not fileLoaded and not dirty:
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


def prompt(message):
    buf = ""
    while True:
        set_status_message(message, buf)
        refresh_screen()
        c = raw_read()
        if c == EditorKeys.BACKSPACE:
            buf = buf[0:-1]
        elif c == ctrl_key('c'):
            set_status_message("")
            return None
        elif c in ('\r', '\n'):
            if len(buf) != 0:
                set_status_message("")
                return buf
        elif type(c) != EditorKeys and not is_ctrl(c) and ord(c) < 128:
            buf += c


""" editor """


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
    if cy == 0 and cx == 0:
        return
    if cx > 0:
        delete_char_at_row(cy, cx - 1)
        cx -= 1
    else:
        cx = len(fileRows[cy-1])
        fileRows[cy-1] += fileRows[cy]
        delete_row(cy)
        cy -= 1


def delete_row(at):
    global fileRows, dirty
    if at < 0 or at >= len(fileRows):
        return
    fileRows = fileRows[0:at] + fileRows[at+1:]
    dirty = True


def insert_row(at, s):
    global fileRows, dirty
    if at < 0 or at > len(fileRows):
        return
    fileRows = fileRows[0:at] + [s] + fileRows[at:]
    dirty = True


def insert_new_line():
    global cx, cy, fileRows
    if cx == 0:
        insert_row(cy, "")
    else:
        insert_row(cy+1, fileRows[cy][cx:])
        fileRows[cy] = fileRows[cy][0:cx]
    cx = 0
    cy += 1


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
    except IOError:
        pexit("error opening %s\n" % filename)
    reset_dirty()


def save_file():
    global fileLoaded, fileRows, file_name, dirty
    if not file_name:
        file_name = prompt("Save as: (CTRL-c to cancel)")
        if not file_name:
            set_status_message("Save aborted")
            return
    try:
        with open(file_name, 'w+') as file:
            text = convert_rows_to_string(fileRows)
            file.write(text)
            fileLoaded = True
            set_status_message("%d bytes written to disk." % len(text))
    except IOError as e:
        set_status_message("Error writing to %s\n - %s" % (file_name, str(e)))
    reset_dirty()
