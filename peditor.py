#!/usr/bin/env python3

"""
peditor.py: main entry point for peditor
"""
from editor import init, read_key, refresh_screen


def main():
    init()
    while True:
        refresh_screen()
        read_key()


if __name__ == "__main__":
    main()
