from config import *
import threading
import time
import curses
import copy
from mylogger import myLogger

from framebuffer import FrameBuffer, MINITEL_COLOR, INIT_CHAR
from terminals.terminal import Terminal
from components.sequence import Sequence


class TerminalCurses(Terminal):
    def __init__(self, framebuffer: FrameBuffer, stdscr):
        super().__init__(framebuffer)
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

            self.color_pairs = {}
            pair_number = 1

            colors = [MINITEL_COLOR.WHITE, MINITEL_COLOR.GREY_1, MINITEL_COLOR.GREY_2, MINITEL_COLOR.GREY_3, MINITEL_COLOR.GREY_4, MINITEL_COLOR.GREY_5, MINITEL_COLOR.GREY_6, MINITEL_COLOR.BLACK]
            curses_colors = [curses.COLOR_WHITE, 240, 242, 244, 246, 248, 250, curses.COLOR_BLACK]
            
            for idx_fg, fg in enumerate(colors):
                for idx_bg, bg in enumerate(colors):
                    curses.init_pair(pair_number, curses_colors[idx_fg], curses_colors[idx_bg])
                    self.color_pairs[(fg, bg)] = pair_number
                    pair_number += 1
            myLogger.log(f"Initialized {pair_number-1} color pairs for curses terminal.")


    def get_input_key(self) -> Sequence|None:
        key = self.stdscr.getch()
        if key != -1:
            # Convert single key to Sequence
            key_sequence = Sequence(key)
            return key_sequence
        else:
            return None
    
    def set_mode(self, mode: int):
        # Curses terminal mode change (0=40 cols, 1=80 cols)
        #if mode == 0:
        #    self.stdscr.resize(HEIGHT, 40)
        #else:
        #    self.stdscr.resize(HEIGHT, 80)
        self.stdscr.clear()

    def draw_buffer(self):
        n = 0

        # Stream current screen to the terminal
        # NOTE: We copy it for now
        # NOTE: Lock it so we have a clean copy
        self.framebuffer.screen_lock.acquire()
        screen_copy = copy.deepcopy(self.framebuffer.screen)
        self.framebuffer.screen_lock.release()
        for y, row in enumerate(screen_copy):
            for x, cell in enumerate(row):
                if cell.a_char != cell.b_char or cell.a_char.attr != cell.b_char.attr:
                    # grab color pre-defined in curses
                    # based on the enum value
                    color_idx = self.color_pairs.get(
                        (cell.b_char.attr.char_color, 
                         cell.b_char.attr.background_color), 0)
                    
                    attributes = 0
                    if cell.b_char.attr.underline:
                        attributes |= curses.A_UNDERLINE
                    if cell.b_char.attr.blinking:
                        attributes |= curses.A_BLINK
                    if cell.b_char.attr.inverted:
                        attributes |= curses.A_REVERSE

                    # print
                    char = cell.b_char.char
                    if char == INIT_CHAR:
                        char = ' '
                    self.stdscr.addch(y, x, char, curses.color_pair(color_idx) | attributes)

                    # simulate slow drawing
                    time.sleep(CURSES_WAIT_TIME)

                    n += 1

        # NOTE: update the screen, indicate what we have written
        # NOTE: Lock probably not needed here
        self.framebuffer.screen_lock.acquire()
        for y, row in enumerate(screen_copy):
            for x, char in enumerate(row):
                self.framebuffer.screen[y][x].a_char.char = char.b_char.char
                self.framebuffer.screen[y][x].a_char.attr.char_color = char.b_char.attr.char_color
                self.framebuffer.screen[y][x].a_char.attr.background_color = char.b_char.attr.background_color
                self.framebuffer.screen[y][x].a_char.attr.size = char.b_char.attr.size
                self.framebuffer.screen[y][x].a_char.attr.underline = char.b_char.attr.underline
                self.framebuffer.screen[y][x].a_char.attr.blinking = char.b_char.attr.blinking
                self.framebuffer.screen[y][x].a_char.attr.inverted = char.b_char.attr.inverted
                self.framebuffer.screen[y][x].a_char.attr.z = char.b_char.attr.z
                self.framebuffer.screen[y][x].a_char.attr.order = char.b_char.attr.order

        self.framebuffer.screen_lock.release()

        #myLogger.log(f"Redrew {n} chars")
        self.stdscr.refresh()
