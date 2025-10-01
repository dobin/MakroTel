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
    page: Page = PageA(terminal.framebuffer)
    terminal.SetPage(page)

    while True:
        terminal.Tick()
        time.sleep(REFRESH_TIME)

# Run curses application
curses.wrapper(main)
