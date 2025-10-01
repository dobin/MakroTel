from config import *
from mylogger import myLogger
import threading
import time
from abc import ABC, abstractmethod
from components.sequence import Sequence
from framebuffer import FrameBuffer, Cell
from pages.page import Page
from terminals.terminal import Terminal


class Engine:
    def __init__(self, framebuffer: FrameBuffer, terminal: Terminal):
        self.width: int = WIDTH
        self.height: int = HEIGHT
        self.bg_char: str = CHAR_BG
        self.framebuffer = framebuffer
        self.running = True  # Flag to control the draw loop
        self.terminal = terminal
        self.page: Page|None = None

        threading.Thread(target=self.draw_loop, daemon=True).start()


    def SetPage(self, page: Page):
        self.page = page
        self.page.initial()


    def Tick(self):
        if self.page is None:
            return
        self.page.Tick()
        keySequence = self.terminal.get_input_key()
        if keySequence is not None:
            self.page.KeyPressed(keySequence)


    def draw_loop(self):
        while self.running:
            # Wait for the event to be set, with a timeout for periodic refresh
            self.framebuffer.draw_event.wait(timeout=1.0)  # 1 second timeout as fallback
            
            if self.running:  # Check if we should still be running
                self.terminal.draw_buffer()
                self.framebuffer.draw_event.clear()  # Reset the event after drawing
