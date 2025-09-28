from config import HEIGHT
from pages.page import Page

from terminals.terminal import Terminal
from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover


class PageA(Page):
    def __init__(self, terminal: Terminal):
        super().__init__(terminal)
        self.components: list = []
        self.x: int = 0
        self.y: int = HEIGHT // 2
        self.dx: int = 1

        self.components.append(ComponentClock(terminal, 1, 0))
        self.components.append(ComponentText(terminal, 10, 1, "MakroTel"))
        self.components.append(ComponentMover(terminal, 1, 2))


    def initial(self):
        self.terminal.clear_buffer()

        for component in self.components:
            component.Initial()


    def Tick(self):
        self.terminal.clear_buffer()

        for component in self.components:
            component.Tick()


    def KeyPressed(self, key: int):
        for component in self.components:
            component.KeyPressed(key)