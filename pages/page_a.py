from config import HEIGHT
from pages.page import Page
from components.sequence import Sequence

from terminals.terminal import Terminal
from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField

class PageA(Page):
    def __init__(self, terminal: Terminal):
        super().__init__(terminal)
        self.components: list = []
        self.x: int = 0
        self.y: int = HEIGHT // 2
        self.dx: int = 1

        self.components.append(ComponentClock(terminal, 1, 0))
        self.components.append(ComponentText(terminal, 12, 0, "MakroTel"))
        self.components.append(ComponentMover(terminal, 1, 1))
        self.components.append(ComponentTextField(terminal, 15, 2, 20))
        self.components.append(ComponentMenu(terminal, ["Item 1", "Item 2", "Item 3"], 1, 4))


    def initial(self):
        self.terminal.clear_buffer()

        for component in self.components:
            component.Initial()


    def Tick(self):
        self.terminal.clear_buffer()

        for component in self.components:
            component.Tick()


    def KeyPressed(self, keys: Sequence):
        for component in self.components:
            component.KeyPressed(keys)

            