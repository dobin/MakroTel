from config import *
from mylogger import myLogger
import threading
import time


class Cell:
    def __init__(self):
        # current, drawn
        self.a_char: str = ' '
        self.a_color = 0

        # new, to draw
        self.b_char: str = ' '
        self.b_color = 0
        self.b_type = 0


    def Set(self, char: str, color=0, type=0):
        self.b_char = char
        self.b_color = color
        self.b_type = type
        

class Terminal:
    def __init__(self):
        self.width: int = WIDTH
        self.height: int = HEIGHT
        self.bg_char: str = CHAR_BG
        self.screen: list[list[Cell]] = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.screen_lock = threading.Lock()


    def draw_buffer(self):
        pass


    def set_char(self, x: int, y: int, char: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen[y][x].Set(char)


    def clear_buffer(self):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x].Set(self.bg_char)



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
        myLogger.log("Beep not available")
