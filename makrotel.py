import curses
import time

from config import *
config_set_mode("curses")

from mylogger import myLogger
from terminals.terminal_curses import TerminalCurses
from terminals.terminal import Terminal
from pages.page import Page
from pages.page_a import PageA
from pages.page_b import PageB
from pages.page_meditations import PageMeditations
from components.sequence import Sequence
from engine import Engine
from framebuffer import FrameBuffer


def main(stdscr):
    framebuffer = FrameBuffer()
    terminal: Terminal = TerminalCurses(framebuffer, stdscr)
    engine = Engine(framebuffer, terminal)

    pagea: Page = PageA(framebuffer)
    pageb: Page = PageB(framebuffer)
    pagemeditations: Page = PageMeditations(framebuffer)
    engine.pageManager.add_page("PageA", pagea)
    engine.pageManager.add_page("PageB", pageb)
    engine.pageManager.add_page("Meditations", pagemeditations)
    engine.pageManager.set_current_page("Meditations")

    while True:
        engine.Tick()
        time.sleep(REFRESH_TIME)

# Run curses application
curses.wrapper(main)
