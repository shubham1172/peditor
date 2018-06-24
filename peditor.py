#!/usr/bin/env python3

"""
peditor.py: main entry point for peditor
"""
from utils import getch, pprint

__version__ = "0.0.1"


def main():
    while True:
        c = getch()
        pprint(c, ord(c))
        if c == 'q':
            break


if __name__ == "__main__":
    main()
