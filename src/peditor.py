#!/usr/bin/env python3

"""
peditor.py: main entry point for peditor
"""
import sys
from editor import init, read_key, refresh_screen, load_file, set_status_message


def main():
    init()
    if len(sys.argv) >= 2:
        load_file(sys.argv[1])
    set_status_message("HELP: CTRL-q = quit | CTRL-s = save | CTRL-f = find")
    while True:
        refresh_screen()
        read_key()


if __name__ == "__main__":
    main()
