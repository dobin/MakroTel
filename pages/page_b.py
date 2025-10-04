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


class PageB(Page):
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer)
        self.dx: int = 1

        self.components.append(ComponentClock(framebuffer, 1, 1))
        self.components.append(ComponentText(framebuffer, 12, 1, "MakroTel Page 2"))


        # Create a container at position (5, 5) with size 20x10 and border
        container = ComponentContainer(framebuffer, x=5, y=5, h=10, w=20, border=True)

        # Create child components with container-relative coordinates
        text_component = ComponentText(framebuffer, 0, 0, "Hello Container!")
        menu_component = ComponentMenu(framebuffer, ["Option 1", "Option 2"], 0, 2)

        # Add components to the container (coordinates are relative to container's inner area)
        container.add_component(text_component, relative_x=2, relative_y=1)
        container.add_component(menu_component, relative_x=2, relative_y=3)

        self.components.append(container)
