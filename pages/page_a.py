from config import HEIGHT
from pages.page import Page

from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover


class PageA(Page):
    def __init__(self, screen):
        super().__init__(screen)
        self.components = []
        self.x = 0
        self.y = HEIGHT // 2
        self.dx = 1

        self.components.append(ComponentClock(screen, 1, 0))
        self.components.append(ComponentText(screen, 10, 1, "MakroTel"))
        self.components.append(ComponentMover(screen, 1, 2))


    def initial(self):
        self.screen.clear_buffer()
        self.screen.set_char(self.x, self.y, '@')


    def Tick(self):
        self.screen.clear_buffer()

        for component in self.components:
            component.Tick()

    def KeyPressed(self, key):
        for component in self.components:
            component.KeyPressed(key)