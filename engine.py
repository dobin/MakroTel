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
        self.last_rotation_time: float = time.time()  # Track time for page rotation
        threading.Thread(target=self.draw_loop, daemon=True).start()


    def Tick(self):
        current_page = self.pageManager.get_current_page()
        if current_page is None:
            return
        
        # Check for keyboard input
        keySequence = self.terminal.get_input_key()
        if keySequence is not None:
            # Reset rotation timer on any keyboard input
            self.last_rotation_time = time.time()
            if DEBUG:
                myLogger.log("Engine: Keyboard input detected, resetting rotation timer")
            current_page.KeyPressed(keySequence)
        
        # Check if it's time to rotate to the next page
        if PAGE_ROTATION_INTERVAL > 0 and self.pageManager.is_rotation_enabled():
            current_time = time.time()
            elapsed_time = current_time - self.last_rotation_time
            
            if elapsed_time >= PAGE_ROTATION_INTERVAL:
                if DEBUG:
                    myLogger.log(f"Engine: Rotation interval reached ({elapsed_time:.1f}s), rotating to next page")
                self.pageManager.rotate_to_next_page()
                self.last_rotation_time = current_time
        
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