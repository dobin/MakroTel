from __future__ import annotations  # for Python 3.7+, optional in 3.11+

from components.sequence import Sequence
from framebuffer import FrameBuffer
from terminals.minitel_model import MinitelVideoMode
from config import HEIGHT, DEBUG
from mylogger import myLogger
from constants.keys import CTRL_2, CTRL_4, CTRL_ASCII_2, CTRL_ASCII_4


class PageManager():
    def __init__(self):
        self.current_page: Page|None = None
        self.pages = {}
        self.has_page_changed = False
        self.page_stack = []  # Stack to track page navigation history
        self.rotation_enabled = False
        self.rotation_pages = []  # List of page names to rotate through
        self.rotation_index = 0  # Current index in rotation_pages

    def add_page(self, page: Page):
        pageName = page.name
        self.pages[pageName] = page
        self.pages[pageName].set_page_manager(self)


    # current page
    def set_current_page(self, name: str, pageInput: dict|None = None):
        if name not in self.pages:
            myLogger.log(f"Page '{name}' not found in PageManager.")
            return
        
        # Add current page to stack before switching
        if self.current_page is not None:
            current_page_name = self.current_page.name
            self.page_stack.append(current_page_name)
            if DEBUG:
                myLogger.log(f"PageManager: Added '{current_page_name}' to navigation stack")

        if self.current_page is None:        
            myLogger.log(f"PageManager: To {name}")
        else:
            myLogger.log(f"PageManager: From {self.current_page.name} to {name}")

        self.current_page = self.pages[name]
        if self.current_page is None:
            myLogger.log(f"PageManager: Current page is None after setting to '{name}'")
            return
        self.current_page.set_page_input(pageInput)
        self.set_page_changed(True)

    def get_current_page(self) -> Page|None:
        return self.current_page
    
    def go_back(self) -> bool:
        """Navigate back to the previous page in the stack.
        
        Returns:
            bool: True if navigation was successful, False if no previous page available
        """
        if not self.page_stack:
            myLogger.log("PageManager: No previous page available in navigation stack")
            return False
        
        previous_page_name = self.page_stack.pop()
        if previous_page_name not in self.pages:
            myLogger.log(f"PageManager: Previous page '{previous_page_name}' no longer exists")
            return self.go_back()  # Try the next page in stack
        
        # Set the page directly without adding to stack to avoid infinite loops
        self.current_page = self.pages[previous_page_name]
        myLogger.log(f"PageManager: Navigated back to page: {previous_page_name}")
        self.set_page_changed(True)
        return True

    # has page changed?
    def get_page_changed(self):
        return self.has_page_changed

    def set_page_changed(self, b):
        self.has_page_changed = b

    # Page rotation methods
    def set_rotation_pages(self, page_names: list[str]):
        """Set the list of pages to rotate through.
        
        Args:
            page_names: List of page names in the order they should be displayed
        """
        # Validate that all pages exist
        valid_pages = [name for name in page_names if name in self.pages]
        if len(valid_pages) != len(page_names):
            invalid = set(page_names) - set(valid_pages)
            myLogger.log(f"PageManager: Warning - invalid page names in rotation list: {invalid}")
        
        self.rotation_pages = valid_pages
        self.rotation_index = 0
        myLogger.log(f"PageManager: Set rotation pages: {valid_pages}")

    def enable_rotation(self):
        """Enable automatic page rotation"""
        self.rotation_enabled = True
        myLogger.log("PageManager: Page rotation enabled")

    def disable_rotation(self):
        """Disable automatic page rotation"""
        self.rotation_enabled = False
        myLogger.log("PageManager: Page rotation disabled")

    def is_rotation_enabled(self) -> bool:
        """Check if rotation is enabled"""
        return self.rotation_enabled

    def rotate_to_next_page(self):
        """Rotate to the next page in the rotation list"""
        if not self.rotation_enabled or not self.rotation_pages:
            return
        
        self.rotation_index = (self.rotation_index + 1) % len(self.rotation_pages)
        next_page_name = self.rotation_pages[self.rotation_index]
        
        myLogger.log(f"PageManager: Auto-rotating to page: {next_page_name} (index {self.rotation_index})")
        
        # Use internal navigation without adding to page stack for auto-rotation
        self.current_page = self.pages[next_page_name]
        self.current_page.set_page_input(None)
        self.set_page_changed(True)


class Page:
    def __init__(self, framebuffer: FrameBuffer, name: str, mode: MinitelVideoMode = MinitelVideoMode.VIDEOTEX):
        self.name: str = name
        self.mode: MinitelVideoMode = mode
        self.framebuffer: FrameBuffer = framebuffer
        self.components: list = []
        self.pageManager: PageManager|None = None
        self.pageInput: dict|None = None


    def set_page_input(self, pageInput: dict|None):
        self.pageInput = pageInput

    def get_page_input_once(self) -> dict|None:
        """Retrieve and clear the page input data."""
        temp = self.pageInput
        self.pageInput = None
        return temp

    
    def Initial(self):
        self.framebuffer.clear_buffer()

        for component in self.components:
            component.Initial()

        # Signal that drawing may needed
        self.framebuffer.draw_event.set()


    def Tick(self):
        self.framebuffer.clear_buffer()

        for component in self.components:
            component.Tick()
        
        # Signal that drawing may be required
        # We finished the rendered page
        # There may or may not be changes to the framebuffer
        self.framebuffer.draw_event.set()


    def KeyPressed(self, keys: Sequence):
        if self.pageManager is not None:
            if keys.egale(Sequence(CTRL_2)) or keys.egale(Sequence(CTRL_ASCII_2)):
                self.pageManager.go_back()
            elif keys.egale(Sequence(CTRL_4)) or keys.egale(Sequence(CTRL_ASCII_4)):
                self.pageManager.set_current_page("Overview")

        for component in self.components:
            component.KeyPressed(keys)


    def set_page_manager(self, pageManager: PageManager):
        self.pageManager = pageManager
        for component in self.components:
            component.set_page_manager(pageManager)
