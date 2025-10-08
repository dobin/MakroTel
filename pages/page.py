from __future__ import annotations  # for Python 3.7+, optional in 3.11+

from components.sequence import Sequence
from framebuffer import FrameBuffer
from config import HEIGHT
from mylogger import myLogger


class PageManager():
    def __init__(self):
        self.current_page: Page
        self.pages = {}
        self.has_page_changed = False

    def add_page(self, name: str, page: Page):
        self.pages[name] = page
        self.pages[name].set_page_manager(self)

    def set_current_page(self, name: str):
        if name not in self.pages:
            myLogger.log(f"Page '{name}' not found in PageManager.")
            return
        self.current_page = self.pages[name]
        myLogger.log(f"Switched to page: {name}")
        self.set_page_changed(True)

    def get_page_changed(self):
        return self.has_page_changed

    def set_page_changed(self, b):
        self.has_page_changed = b

    def get_current_page(self) -> Page|None:
        return self.current_page


class Page:
    def __init__(self, framebuffer: FrameBuffer, mode: int = 0):
        self.mode = mode
        self.framebuffer = framebuffer
        self.components: list = []
        self.pageManager: PageManager|None = None

    
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
            if keys.egale(Sequence([0x41])):
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
