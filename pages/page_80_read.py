from config import HEIGHT
from pages.page import Page
from components.sequence import Sequence
from framebuffer import FrameBuffer
from terminals.minitel_model import MinitelVideoMode

from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField
from components.component_container import ComponentContainer
from components.component_textarea import ComponentTextArea

WIDE_WIDTH = 80


class Page80Read(Page):
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name, mode=MinitelVideoMode.TELEMATIC)

        self.textarea = ComponentTextArea(framebuffer, 0, 1, WIDE_WIDTH, HEIGHT-1, "")
        self.components.append(self.textarea)


    def Initial(self):
        super().Initial()

        pageInput: dict|None = self.get_page_input_once()
        if pageInput is not None and "content" in pageInput:
            content = pageInput["content"]
            if isinstance(content, str):
                self.textarea.set_text(content)
