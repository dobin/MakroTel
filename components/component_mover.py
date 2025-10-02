from config import *
from components.component import Component
from components.sequence import Sequence
from constants.keys import KEY_UP, KEY_DOWN

class ComponentMover(Component):
    def __init__(self, framebuffer, x: int, y: int):
        super().__init__(framebuffer, x, y, 1, 1)
        self.dx: int = 1


    def Initial(self):
        self.framebuffer.set_char(self.x, self.y, '@')


    def Tick(self):
        self.x += self.dx
        if self.x >= WIDTH or self.x < 0:
            self.dx *= -1
            self.x += self.dx  # Bounce back
        self.framebuffer.set_char(self.x, self.y, '@')


    def KeyPressed(self, keys: Sequence):
        if keys.egale(KEY_UP) and self.y > 0:
            self.y -= 1
        elif keys.egale(KEY_DOWN) and self.y < HEIGHT - 1:
            self.y += 1