import curses
import time

from config import *
config_set_mode("curses")

from mylogger import myLogger
from terminals.terminal_curses import TerminalCurses
from terminals.terminal import Terminal
from pages.page import Page
from pages.page_a import PageA
from engine import Engine
from framebuffer import FrameBuffer


def main(stdscr):
    framebuffer = FrameBuffer()
    terminal: Terminal = TerminalCurses(framebuffer, stdscr)
    engine = Engine(framebuffer, terminal)
    page: Page = PageA(framebuffer)

    engine.SetPage(page)
    while True:
        engine.Tick()
        time.sleep(REFRESH_TIME)

# Run curses application
curses.wrapper(main)
