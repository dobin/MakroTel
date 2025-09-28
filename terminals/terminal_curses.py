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
        super().__init__(stdscr)
        self.screen_lock = threading.Lock()
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

    def position(self, x, y):
        """Set cursor position (1-based coordinates like Minitel)"""
        # Convert from 1-based to 0-based coordinates
        self.cursor_x = max(1, min(x, self.width))
        self.cursor_y = max(1, min(y, self.height))
        # Note: We don't move the actual cursor here, just track position
        # The actual positioning happens in send() method

    def send(self, data):
        """Send data to the terminal at current cursor position"""
        with self.screen_lock:
            try:
                # Handle different data types
                if isinstance(data, str):
                    # String data
                    for char in data:
                        self._put_char_at_cursor(char)
                elif isinstance(data, list):
                    # List of characters or byte values
                    for item in data:
                        if isinstance(item, int):
                            # Convert byte value to character
                            if 0 <= item <= 255:
                                char = chr(item) if item >= 32 and item < 127 else '?'
                                self._put_char_at_cursor(char)
                        elif isinstance(item, str):
                            for char in item:
                                self._put_char_at_cursor(char)
                elif isinstance(data, int):
                    # Single byte value
                    if 0 <= data <= 255:
                        char = chr(data) if data >= 32 and data < 127 else '?'
                        self._put_char_at_cursor(char)
            except Exception as e:
                myLogger.log(f"Error in send: {e}")

    def _put_char_at_cursor(self, char):
        """Internal method to put a character at current cursor position"""
        if 0 <= self.cursor_x - 1 < self.width and 0 <= self.cursor_y - 1 < self.height:
            self.screen[self.cursor_y - 1][self.cursor_x - 1].Set(char)
            self.cursor_x += 1
            if self.cursor_x > self.width:
                self.cursor_x = 1
                self.cursor_y += 1
                if self.cursor_y > self.height:
                    self.cursor_y = self.height

    def repeat(self, char, count):
        """Repeat a character a specified number of times"""
        if isinstance(char, int):
            # Convert byte value to character
            if 0 <= char <= 255:
                char = chr(char) if char >= 32 and char < 127 else '?'
            else:
                char = '?'
        
        data = char * count
        self.send(data)

    def repeter(self, char, count):
        """French alias for repeat method"""
        self.repeat(char, count)

    def color(self, character=None, background=None):
        """Set text color"""
        # For now, we'll just track the color but not apply it in curses
        # since the current drawing system doesn't support colors yet
        self.current_color = character
        # Could be extended to use curses color pairs in the future

    def effect(self, invert=None, bold=None, underline=None):
        """Set text effects"""
        if invert is not None:
            self.invert_mode = invert
        # For now, we only track the invert mode
        # The actual invert effect could be implemented by swapping
        # characters or using curses attributes

    def beep(self):
        """Make a beep sound"""
        try:
            curses.beep()
        except:
            # If beep is not available, we could log it
            myLogger.log("Beep not available")
