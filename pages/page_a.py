from config import HEIGHT
from pages.page import Page
from components.sequence import Sequence

from framebuffer import FrameBuffer
from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField


class PageA(Page):
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer)
        self.components: list = []
        self.x: int = 0
        self.y: int = HEIGHT // 2
        self.dx: int = 1

        self.components.append(ComponentClock(framebuffer, 1, 0))
        self.components.append(ComponentText(framebuffer, 12, 0, "MakroTel"))
        self.components.append(ComponentMover(framebuffer, 1, 1))
        self.components.append(ComponentTextField(framebuffer, 15, 2, 20))
        self.components.append(ComponentMenu(framebuffer, ["Item 1", "Item 2", "Item 3"], 1, 4))


    def initial(self):
        self.framebuffer.clear_buffer()

        for component in self.components:
            component.Initial()


    def Tick(self):
        self.framebuffer.clear_buffer()

        for component in self.components:
            component.Tick()


    def KeyPressed(self, keys: Sequence):
        for component in self.components:
            component.KeyPressed(keys)

            