from __future__ import annotations  # for Python 3.7+, optional in 3.11+

from components.sequence import Sequence
from framebuffer import FrameBuffer
from config import HEIGHT
from mylogger import myLogger


class PageManager():
    def __init__(self):
        self.current_page: Page|None = None
        self.pages = {}
        self.has_page_changed = False
        self.page_stack = []  # Stack to track page navigation history

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
            myLogger.log(f"PageManager: Added '{current_page_name}' to navigation stack")
        
        self.current_page = self.pages[name]
        if self.current_page is None:
            myLogger.log(f"PageManager: Current page is None after setting to '{name}'")
            return
        self.current_page.set_page_input(pageInput)
        myLogger.log(f"PageManager: Set new page: {name}")
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


class Page:
    def __init__(self, framebuffer: FrameBuffer, name: str, mode: int = 0):
        self.name = name
        self.mode = mode
        self.framebuffer = framebuffer
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

    
    def initial(self):
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
            # ESC key for back navigation
            if keys.egale(Sequence([0x43])):
                self.pageManager.go_back()
            elif keys.egale(Sequence([0x41])):
                self.pageManager.set_current_page("PageA")
            elif keys.egale(Sequence([0x42])):
                self.pageManager.set_current_page("PageB")
            elif keys.egale(Sequence([ord('O')])) or keys.egale(Sequence([ord('o')])):
                self.pageManager.set_current_page("Overview")

        for component in self.components:
            component.KeyPressed(keys)


    def set_page_manager(self, pageManager: PageManager):
        self.pageManager = pageManager
        for component in self.components:
            component.set_page_manager(pageManager)
