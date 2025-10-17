import threading
import time
from abc import ABC, abstractmethod

from config import *
from mylogger import myLogger
from components.sequence import Sequence
from framebuffer import FrameBuffer
from terminals.minitel_model import MinitelVideoMode


class Terminal:
    def __init__(self, framebuffer: FrameBuffer):
        self.framebuffer = framebuffer


    @abstractmethod
    def draw_buffer(self):
        # draw the framebuffer to the terminal (hardware or curses)
        pass


    @abstractmethod
    def get_input_key(self) -> Sequence|None:
        # read a key from the terminal and return it as a Sequence
        pass


    @abstractmethod
    def set_mode(self, mode: MinitelVideoMode):
        # change the hardware to the specific mode
        pass


    def change_mode(self, mode: MinitelVideoMode):
        myLogger.log(f"Terminal: Change mode to {mode}")

        # notify framebuffer about the size change
        if mode == MinitelVideoMode.VIDEOTEX:
            self.framebuffer.set_width(40)
        elif mode == MinitelVideoMode.TELEMATIC:
            self.framebuffer.set_width(80)

        # notify the hardware
        # video_changed_mode()
        self.set_mode(mode)


    def position(self, x, y):
        """Set cursor position (1-based coordinates like Minitel)"""
        # Convert from 1-based to 0-based coordinates
        self.cursor_x = max(1, min(x, self.framebuffer.width))
        self.cursor_y = max(1, min(y, HEIGHT))
        # Note: We don't move the actual cursor here, just track position
        # The actual positioning happens in send() method


    def send(self, data):
        """Send data to the terminal at current cursor position"""
        with self.framebuffer.screen_lock:
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
        if 0 <= self.cursor_x - 1 < self.framebuffer.width and 0 <= self.cursor_y - 1 < HEIGHT:
            self.framebuffer.screen[self.cursor_y - 1][self.cursor_x - 1].Set(char)
            self.cursor_x += 1
            if self.cursor_x > self.framebuffer.width:
                self.cursor_x = 1
                self.cursor_y += 1
                if self.cursor_y > HEIGHT:
                    self.cursor_y = HEIGHT
