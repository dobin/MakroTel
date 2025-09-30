from config import *
import threading
import time
import curses
import copy
from mylogger import myLogger

from terminals.terminal import Terminal
from components.sequence import Sequence


class TerminalCurses(Terminal):
    def __init__(self, stdscr):
        super().__init__()
        self.stdscr = stdscr
        self.cursor_x = 1
        self.cursor_y = 1
        self.current_color = None
        self.invert_mode = False

        curses.curs_set(0)       # Hide cursor
        stdscr.nodelay(True)     # Non-blocking input
        stdscr.clear()
        
        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # Define color pairs (foreground, background)
            for i in range(1, min(curses.COLORS, 8)):
                curses.init_pair(i, i, -1)


    def draw_buffer(self):
        n = 0

        # Stream current screen to the terminal
        # NOTE: We copy it for now
        # NOTE: Lock it so we have a clean copy
        self.framebuffer.screen_lock.acquire()
        screen_copy = copy.deepcopy(self.framebuffer.screen)
        self.framebuffer.screen_lock.release()
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
        self.framebuffer.screen_lock.acquire()
        for y, row in enumerate(screen_copy):
            for x, char in enumerate(row):
                self.framebuffer.screen[y][x].a_char = char.b_char
                self.framebuffer.screen[y][x].a_color = char.b_color
        self.framebuffer.screen_lock.release()

        #myLogger.log(f"Redrew {n} chars")
        self.stdscr.refresh()
