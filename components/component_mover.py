from config import *
from components.component import Component
from components.sequence import Sequence

from config import MODE
if MODE == "minitel":
    from terminals.minitel_constants import UP, DOWN
    KEY_UP = UP
    KEY_DOWN = DOWN
else:
    import curses
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN

class ComponentMover(Component):
    def __init__(self, terminal, x: int, y: int):
        super().__init__(terminal, x, y, 1, 1)
        self.dx: int = 1


    def Initial(self):
        self.terminal.set_char(self.x, self.y, '@')


    def Tick(self):
        self.x += self.dx
        if self.x >= WIDTH or self.x < 0:
            self.dx *= -1
            self.x += self.dx  # Bounce back
        self.terminal.set_char(self.x, self.y, '@')


    def KeyPressed(self, keys: Sequence):
        if keys.egale(KEY_UP) and self.y > 0:
            self.y -= 1
        elif keys.egale(KEY_DOWN) and self.y < HEIGHT - 1:
            self.y += 1