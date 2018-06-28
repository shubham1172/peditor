"""
editor.py: editor functions
"""
import time
import re
from keys import EditorKeys
from utils import getch, is_ctrl, ctrl_key, pexit, pprint, get_terminal_size, \
    convert_rows_to_string, convert_string_to_rows
from syntax import syntax


def init():
    global screen_rows, screen_cols, cx, cy, \
        file_loaded, file_rows, row_offset, column_offset, \
        file_name, file_type, status_message, status_message_time, \
        dirty, quit_times, last_match, direction
    cx, cy = 0, 0           # curr cursor location
    screen_rows, screen_cols = get_terminal_size()
    screen_rows -= 2        # status and message bar
    file_loaded = False
    file_type = None
    file_rows = []
    row_offset = 0          # row coefficient
    column_offset = 0       # col coefficient
    file_name = None
    status_message = ""
    status_message_time = 0
    dirty = False           # indicate that file is modified
    quit_times = 3          # number of times to press quit for closing dirty files
    last_match = (0, -1)    # last match index (row, col)
    direction = 1           # default search direction


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
    global screen_rows, screen_cols, cx, cy, row_offset, file_rows, dirty, quit_times
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
    elif c == ctrl_key('f'):
        search()
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
            cy = row_offset
        times = screen_rows
        while times > 0:
            move_cursor(EditorKeys.ARROW_UP if c == EditorKeys.PAGE_UP
                        else EditorKeys.ARROW_DOWN)
            times -= 1
    elif c == EditorKeys.HOME_KEY:
        cx = 0
    elif c == EditorKeys.END_KEY:
        if cy < len(file_rows):
            cx = len(file_rows[cy])
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
    global cy, row_offset, screen_rows, \
            cx, column_offset, screen_cols
    if cy < row_offset:
        row_offset = cy
    if cy >= (row_offset + screen_rows):
        row_offset = cy - screen_rows + 1
    if cx < column_offset:
        column_offset = cx
    if cx >= (column_offset + screen_cols):
        column_offset = cx - screen_cols + 1


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
    global screen_rows, screen_cols, file_loaded, file_rows, row_offset, column_offset, dirty
    welcome_message = "peditor -- welcome"
    for row in range(screen_rows):
        file_row = row + row_offset
        if file_row < len(file_rows):
            render_row(file_rows[file_row][column_offset:column_offset+screen_cols])
        if row == screen_rows//3 and not file_loaded and not dirty:
            pad_string = " "*((screen_cols - len(welcome_message)) // 2)
            pprint(pad_string, welcome_message)
        pprint("\n")


def draw_status_bar():
    global file_name, screen_cols, file_rows, cy, dirty, file_type
    pprint("\x1b[7m")  # invert colors
    s = file_name if file_name else "[No Name]"
    left = "%s - %d lines %s" % (s[0:20],
                                 len(file_rows),
                                 "(modified)" if dirty else "")
    right = "%d/%d" % (cy + 1, len(file_rows))
    pad = " "*(screen_cols-len(left)-len(right))
    display_string = left + pad + right
    pprint(display_string[0:screen_cols])
    pprint("\x1b[m")   # restore colors
    pprint("\n")


def set_status_message(*args):
    global status_message, status_message_time
    status_message = " ".join(args)
    status_message_time = time.time()


def draw_message_bar():
    global status_message, status_message_time, screen_cols
    pprint("\x1b[K")    # clear the line
    if (time.time() - status_message_time) < 5:
        pprint(status_message[0:screen_cols])


def prompt(message, callback):
    buf = ""
    while True:
        set_status_message(message % buf)
        refresh_screen()
        c = raw_read()
        if c == EditorKeys.BACKSPACE:
            buf = buf[0:-1]
        elif c == ctrl_key('c'):
            set_status_message("")
            if callback:
                callback(buf, c)
            return None
        elif c in ('\r', '\n'):
            if len(buf) != 0:
                set_status_message("")
                if callback:
                    callback(buf, c)
                return buf
        elif type(c) != EditorKeys and not is_ctrl(c) and ord(c) < 128:
            buf += c

        if callback:
            callback(buf, c)


""" syntax highlighting """


def render_row(row):
    global file_type
    tokens = re.split(r'(\s?)', row)
    comment = False
    string = False
    for token in tokens:
        if file_type and file_type in syntax.keys():
            if comment:
                printf(token, color='red')
            elif string:
                printf(token, color='green')
            elif token == syntax[file_type]["comment"]:
                printf(token, color='red')
                comment = True
            elif token in syntax[file_type]["keywords"]:
                printf(token, color='yellow')
            else:
                for c in token:
                    if c.isdigit():
                        printf(c, color='blue')
                    else:
                        printf(c)
        else:
            pprint(token)


def printf(s, color=None):
    code = 0
    if color == 'red':
        code = 1
    elif color == 'green':
        code = 2
    elif color == 'yellow':
        code = 3
    elif color == 'blue':
        code = 4
    pre = '\x1b[3%dm' % code
    suf = '\x1b[39m'
    if color:
        pprint("%s%s%s" % (pre, s, suf))
    else:
        pprint(s)


""" search """


def search():
    global cx, cy, row_offset, column_offset
    # save the values
    tcx = cx
    tcy = cy
    t_row_offset = row_offset
    t_column_offset = column_offset
    query = prompt("Search: %s (CTRL-c to cancel)", search_callback)
    if not query:
        # restore
        cx = tcx
        cy = tcy
        row_offset = t_row_offset
        column_offset = t_column_offset


def search_callback(query, char):
    global cx, cy, column_offset, row_offset, screen_cols, file_rows, last_match, direction
    if char in ('\r', '\n', ctrl_key('c')):
        last_match = (0, -1)
        direction = 1
        return
    elif char in (EditorKeys.ARROW_RIGHT, EditorKeys.ARROW_DOWN):
        direction = 1
    elif char in (EditorKeys.ARROW_LEFT, EditorKeys.ARROW_UP):
        direction = -1
    else:   # characters
        last_match = (0, -1)
        direction = 1

    """
    last_match[0] gives us the row we need to search in for
    last_match[1] gives us the starting point for the search
    direction decides which part of the row is to be searched
    """
    if last_match == (0, -1):
        direction = 1
    curr = last_match[0]
    counter = 0
    while True:
        if counter == len(file_rows)-1:
            break
        if curr == -1:
            curr = len(file_rows) - 1
        elif curr == len(file_rows):
            curr = 0

        row = file_rows[curr]
        off = 0
        if direction == 1:
            s = row[last_match[1]+1:]
            idx = s.lower().find(query.lower())
            off = last_match[1]+1
        else:
            s = row[0:last_match[1]]
            idx = s.lower().rfind(query.lower())
        if idx > 0:
            last_match = (curr, idx+off)
            cy = curr
            cx = last_match[1]
            # adjust offsets
            if (cx - column_offset) > (screen_cols - 5):
                column_offset = cx
            row_offset = cy
            break
        else:
            curr += direction
            counter += 1
            last_match = (last_match[0], -1)


""" editor """


def insert_char_at_row(row, at, c):
    global file_rows, dirty
    if at < 0 or at > len(file_rows[row]):
        at = len(file_rows[row])
    file_rows[row] = file_rows[row][0:at] + c + file_rows[row][at:]
    dirty = True


def insert_char(c):
    global cx, cy, file_rows
    if cy == len(file_rows):
        file_rows.append("")
    insert_char_at_row(cy, cx, c)
    cx += 1


def delete_char_at_row(row, at):
    global file_rows, dirty
    if at < 0 or at >= len(file_rows[row]):
        return
    file_rows[row] = file_rows[row][0:at] + file_rows[row][at+1:]
    dirty = True


def delete_char():
    global cx, cy, file_rows
    if cy == len(file_rows):
        return
    if cy == 0 and cx == 0:
        return
    if cx > 0:
        delete_char_at_row(cy, cx - 1)
        cx -= 1
    else:
        cx = len(file_rows[cy-1])
        file_rows[cy-1] += file_rows[cy]
        delete_row(cy)
        cy -= 1


def delete_row(at):
    global file_rows, dirty
    if at < 0 or at >= len(file_rows):
        return
    file_rows = file_rows[0:at] + file_rows[at+1:]
    dirty = True


def insert_row(at, s):
    global file_rows, dirty
    if at < 0 or at > len(file_rows):
        return
    file_rows = file_rows[0:at] + [s] + file_rows[at:]
    dirty = True


def insert_new_line():
    global cx, cy, file_rows
    if cx == 0:
        insert_row(cy, "")
    else:
        insert_row(cy+1, file_rows[cy][cx:])
        file_rows[cy] = file_rows[cy][0:cx]
    cx = 0
    cy += 1


""" cursor """


def move_cursor(c):
    global cx, cy, screen_rows, screen_cols, row_offset, column_offset, file_rows

    row = None if cy >= len(file_rows) else file_rows[cy]

    if c == EditorKeys.ARROW_UP:
        if cy != 0:
            cy -= 1
    elif c == EditorKeys.ARROW_DOWN:
        if cy < len(file_rows) - 1:
            cy += 1
    elif c == EditorKeys.ARROW_LEFT:
        if cx != 0:
            cx -= 1
        elif cy > 0:
            cy -= 1
            cx = len(file_rows[cy])
    elif c == EditorKeys.ARROW_RIGHT:
        if row and cx < len(file_rows[cy]):
            cx += 1
        elif row and cy < len(file_rows):
            cy += 1
            cx = 0

    row = "" if cy >= len(file_rows) else file_rows[cy]

    if cx > len(row):
        cx = len(row)


def update_cursor():
    global cx, cy, row_offset, column_offset
    pprint("\x1b[%d;%dH" % (cy - row_offset + 1, cx - column_offset + 1))


""" file handling """


def load_file(filename):
    global file_loaded, file_rows, file_name, file_type
    try:
        with open(filename, 'a+') as file:
            file.seek(0, 0)
            file_rows = convert_string_to_rows(file.read())
        file_loaded = True
        file_name = filename
        file_type = file_name.split(".")[-1]
    except IOError:
        pexit("error opening %s: file doesn't exist or cannot be opened.\n" % filename)
    reset_dirty()


def save_file():
    global file_loaded, file_rows, file_name, file_type
    if not file_name:
        file_name = prompt("Save as: %s (CTRL-c to cancel)", None)
        if not file_name:
            set_status_message("Save aborted")
            return
    try:
        with open(file_name, 'w+') as file:
            text = convert_rows_to_string(file_rows)
            file.write(text)
            file_loaded = True
            file_type = file_name.split(".")[-1]
            set_status_message("%d bytes written to disk." % len(text))
    except IOError as e:
        set_status_message("Error writing to %s\n - %s" % (file_name, str(e)))
    reset_dirty()
