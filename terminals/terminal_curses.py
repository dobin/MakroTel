from config import *
import threading
import time
import curses
import copy
from mylogger import myLogger

from terminals.terminal import Terminal


class Cell:
    def __init__(self):
        # current, drawn
        self.a_char: str = ''
        self.a_color = 0

        # new, to draw
        self.b_char: str = ''
        self.b_color = 0
        self.b_type = 0


    def Set(self, char: str, color=0, type=0):
        self.b_char = char
        self.b_color = color
        self.b_type = type
        

class TerminalCurses(Terminal):
    def __init__(self, stdscr):
        self.width: int = WIDTH
        self.height: int = HEIGHT
        self.bg_char: str = CHAR_BG
        self.screen: list[list[Cell]] = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
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
                    time.sleep(0.02)

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


    def set_char(self, x: int, y: int, char: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen[y][x].Set(char)


    def clear_buffer(self):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x].Set(self.bg_char)
