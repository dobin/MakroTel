from config import HEIGHT
from pages.page import Page
from components.sequence import Sequence

from framebuffer import FrameBuffer
from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField
from components.component_container import ComponentContainer
from components.component_textarea import ComponentTextArea

WIDE_WIDTH = 80


class Page80Read(Page):
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer, mode=1)

        str = "A" * 80
        textarea = ComponentTextArea(framebuffer, 0, 1, WIDE_WIDTH, HEIGHT-1, str)

        self.components.append(textarea)
