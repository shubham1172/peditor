"""
utils.py: Utilities for peditor
"""
import sys
import tty
import termios


def pprint(*args, file=sys.stdout):
    print(*args, end='', file=file, flush=True)


def pexit(message):
    pprint(message, file=sys.stderr)
    sys.exit(0)


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
