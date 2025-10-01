from config import HEIGHT
from pages.page import Page
from components.sequence import Sequence

from framebuffer import FrameBuffer
from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField


class PageB(Page):
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer)
        self.dx: int = 1

        self.components.append(ComponentClock(framebuffer, 1, 0))
        self.components.append(ComponentText(framebuffer, 12, 0, "MakroTel Page 2"))
