"""
utils.py: utilities for peditor
"""
import sys
import tty
import termios
import os


# custom print function
def pprint(*args, file=sys.stdout):
    print(*args, end='', file=file, flush=True)


# exit the editor gracefully
def pexit(message=None):
    pprint("\x1b[2J")  # clear entire screen
    pprint("\x1b[H")   # reposition cursor
    if message:
        pprint(message, file=sys.stderr)
    sys.exit(0)


# check if x is a control key
def is_ctrl(char):
    return 0 <= ord(char) <= 31


# for x, return CTRL(x)'s ascii
def ctrl_key(char):
    return chr(ord(char) & 0x1F)


# read one character
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    ch = None
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    except:
        pexit("error reading from STDIN")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


# get rows, cols
def get_terminal_size():
    s = list(map(int, os.popen('stty size', 'r').read().split()))
    if not s:
        s = [24, 80]
    return s


# convert string to rows
def convert_string_to_rows(s):
    return s.split('\n')

# convert rows to string
def convert_rows_to_string(rows):
    return '\n'.join(rows)