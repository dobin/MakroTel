import curses
import time
import threading
import copy

from config import *
from mylogger import myLogger
from screen import ScreenCurses
from pages.page_a import PageA


def main(stdscr):
    screen = ScreenCurses(stdscr)

    def draw_loop():
        while True:
            screen.draw_buffer()
            time.sleep(0.1)
    threading.Thread(target=draw_loop, daemon=True).start()

    page = PageA(screen)
    page.initial()

    while True:
        page.Tick()

        # Handle input
        key = screen.stdscr.getch()
        if key == ord('q'):
            return
        if key != -1:
            page.KeyPressed(key)

        time.sleep(REFRESH_TIME)


# Run curses application
curses.wrapper(main)
