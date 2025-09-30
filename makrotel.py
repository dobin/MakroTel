import curses
import time
import threading
import copy

from config import *
config_set_mode("curses")

from mylogger import myLogger
from terminals.terminal_curses import TerminalCurses
from terminals.terminal import Terminal
from pages.page import Page
from pages.page_a import PageA
from components.sequence import Sequence


def main(stdscr):
    terminal: Terminal = TerminalCurses(stdscr)

    page: Page = PageA(terminal)
    page.initial()

    while True:
        page.Tick()
        # Signal that drawing is needed after sending data
        terminal.draw_event.set()

        # Handle input
        key = terminal.stdscr.getch()
        if key == ord('q'):
            return
        if key != -1:
            # Convert single key to Sequence
            key_sequence = Sequence(key)
            page.KeyPressed(key_sequence)

        time.sleep(REFRESH_TIME)


# Run curses application
curses.wrapper(main)
