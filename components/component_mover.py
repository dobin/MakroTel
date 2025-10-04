from config import *
from components.component import Component
from components.sequence import Sequence
from constants.keys import KEY_UP, KEY_DOWN

class ComponentMover(Component):
    def __init__(self, framebuffer, x: int, y: int):
        super().__init__(framebuffer, x, y, 1, 1)
        self.dx: int = 1


    def Initial(self):
        self._draw_mover()


    def Tick(self):
        self.x += self.dx
        if self.x >= WIDTH or self.x < 0:
            self.dx *= -1
            self.x += self.dx  # Bounce back
        self._draw_mover()


    def _draw_mover(self):
        self.framebuffer.screen_lock.acquire()
        self.framebuffer.set_char(self.x, self.y, '@')
        self.framebuffer.screen_lock.release()

    def KeyPressed(self, keys: Sequence):
        if keys.egale(KEY_UP) and self.y > 0:
            self.y -= 1
        elif keys.egale(KEY_DOWN) and self.y < HEIGHT - 1:
            self.y += 1