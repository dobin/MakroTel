import threading
import time
from abc import ABC, abstractmethod

from config import *
from mylogger import myLogger
from framebuffer import FrameBuffer, Cell
from pages.page import Page, PageManager
from terminals.terminal import Terminal
from terminals.minitel_model import MinitelVideoMode


class Engine:
    def __init__(self, framebuffer: FrameBuffer, terminal: Terminal):
        self.framebuffer: FrameBuffer = framebuffer
        self.running: bool = True  # Flag to control the draw loop
        self.terminal: Terminal = terminal
        self.pageManager: PageManager = PageManager()
        self.current_mode: MinitelVideoMode = MinitelVideoMode.VIDEOTEX
        threading.Thread(target=self.draw_loop, daemon=True).start()


    def Tick(self):
        current_page = self.pageManager.get_current_page()
        if current_page is None:
            return
        
        keySequence = self.terminal.get_input_key()
        if keySequence is not None:
            current_page.KeyPressed(keySequence)
        current_page.Tick()


    def draw_loop(self):
        while self.running:
            # handle page changes
            # - before draw_event.wait() 
            # - pageManager.Initial() will notify us
            if self.pageManager.get_page_changed():
                if DEBUG:
                    myLogger.log("Engine: got new page")
                self.pageManager.set_page_changed(False)
                current_page = self.pageManager.get_current_page()
                if current_page is None:
                    return
                
                # change width 40/80 if needed
                if DEBUG:
                    myLogger.log("Engine: Change video mode")
                if self.current_mode != current_page.mode:
                    self.current_mode = current_page.mode
                    self.terminal.change_mode(self.current_mode)

                    # Minitel terminal will clear screen itself
                    self.framebuffer.reset_buffer()

                if DEBUG:
                    myLogger.log("Engine: new page initial()")
                current_page.Initial()

            self.framebuffer.draw_event.wait()

            if self.running:  # Check if we should still be running
                # log time taken for performance monitoring in high precision
                start_time = time.perf_counter()
                self.terminal.draw_buffer()
                end_time = time.perf_counter()
                #if DEBUG:
                #    myLogger.log(f"Draw time: {end_time - start_time:.6f} seconds")
                self.framebuffer.draw_event.clear()  # Reset the event after drawing


    def stop(self):
        """Stop the drawing loop gracefully"""
        self.running = False