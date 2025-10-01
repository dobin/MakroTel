from config import *
from mylogger import myLogger
import threading
import time
from abc import ABC, abstractmethod
from components.sequence import Sequence
from framebuffer import FrameBuffer, Cell
from pages.page import Page, PageManager
from terminals.terminal import Terminal


class Engine:
    def __init__(self, framebuffer: FrameBuffer, terminal: Terminal):
        self.framebuffer = framebuffer
        self.running = True  # Flag to control the draw loop
        self.terminal = terminal
        self.pageManager = PageManager()
        threading.Thread(target=self.draw_loop, daemon=True).start()


    def Tick(self):
        current_page = self.pageManager.get_current_page()
        if current_page is None:
            return
        
        current_page.Tick()

        keySequence = self.terminal.get_input_key()
        if keySequence is not None:
            current_page.KeyPressed(keySequence)


    def draw_loop(self):
        while self.running:
            # Wait for the event to be set, with a timeout for periodic refresh
            self.framebuffer.draw_event.wait(timeout=1.0)  # 1 second timeout as fallback
            
            if self.running:  # Check if we should still be running
                self.terminal.draw_buffer()
                self.framebuffer.draw_event.clear()  # Reset the event after drawing


    def stop(self):
        """Stop the drawing loop gracefully"""
        self.running = False