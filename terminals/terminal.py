from config import *
from mylogger import myLogger
import threading
import time


from framebuffer import FrameBuffer, Cell


class Terminal:
    def __init__(self):
        self.width: int = WIDTH
        self.height: int = HEIGHT
        self.bg_char: str = CHAR_BG
        #self.screen: list[list[Cell]] = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        #self.screen_lock = threading.Lock()
        #self.draw_event = threading.Event()  # Event to signal when drawing is needed
        self.framebuffer = FrameBuffer()
        self.running = True  # Flag to control the draw loop

        threading.Thread(target=self.draw_loop, daemon=True).start()


    def draw_loop(self):
        while self.running:
            # Wait for the event to be set, with a timeout for periodic refresh
            self.framebuffer.draw_event.wait(timeout=1.0)  # 1 second timeout as fallback
            
            if self.running:  # Check if we should still be running
                self.draw_buffer()
                self.framebuffer.draw_event.clear()  # Reset the event after drawing

    def draw_buffer(self):
        pass


    def position(self, x, y):
        """Set cursor position (1-based coordinates like Minitel)"""
        # Convert from 1-based to 0-based coordinates
        self.cursor_x = max(1, min(x, self.width))
        self.cursor_y = max(1, min(y, self.height))
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
        if 0 <= self.cursor_x - 1 < self.width and 0 <= self.cursor_y - 1 < self.height:
            self.framebuffer.screen[self.cursor_y - 1][self.cursor_x - 1].Set(char)
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

    def stop(self):
        """Stop the drawing loop gracefully"""
        self.running = False
