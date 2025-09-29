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


def main(stdscr):
    terminal: Terminal = TerminalCurses(stdscr)

    def draw_loop():
        while True:
            terminal.draw_buffer()
            time.sleep(0.1)
    threading.Thread(target=draw_loop, daemon=True).start()

    page: Page = PageA(terminal)
    page.initial()

    while True:
        page.Tick()

        # Handle input
        key = terminal.stdscr.getch()
        if key == ord('q'):
            return
        if key != -1:
            page.KeyPressed(key)

        time.sleep(REFRESH_TIME)


# Run curses application
curses.wrapper(main)
