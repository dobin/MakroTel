from config import *
import threading
import time
import curses
import copy
from mylogger import myLogger

from terminals.terminal import Terminal


class TerminalCurses(Terminal):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.screen_lock = threading.Lock()
        self.stdscr = stdscr

        curses.curs_set(0)       # Hide cursor
        stdscr.nodelay(True)     # Non-blocking input
        stdscr.clear()


    def draw_buffer(self):
        n = 0

        # Stream current screen to the terminal
        # NOTE: We copy it for now
        # NOTE: Lock it so we have a clean copy
        self.screen_lock.acquire()
        screen_copy = copy.deepcopy(self.screen)
        self.screen_lock.release()
        for y, row in enumerate(screen_copy):
            for x, char in enumerate(row):
                if char.a_char != char.b_char:
                    # print
                    self.stdscr.addch(y, x, char.b_char)

                    # simulate slow drawing
                    time.sleep(CURSES_WAIT_TIME)

                    n += 1

        # NOTE: update the screen, indicate what we have written
        # NOTE: Lock probably not needed here
        self.screen_lock.acquire()
        for y, row in enumerate(screen_copy):
            for x, char in enumerate(row):
                self.screen[y][x].a_char = char.b_char
                self.screen[y][x].a_color = char.b_color
        self.screen_lock.release()

        #myLogger.log(f"Redrew {n} chars")
        self.stdscr.refresh()
