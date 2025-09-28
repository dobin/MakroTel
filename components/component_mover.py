from config import *
import curses
from components.component import Component


class ComponentMover(Component):
    def __init__(self, screen, x, y):
        super().__init__(screen, x, y, 1, 1)
        self.dx = 1


    def Tick(self):
        self.x += self.dx
        if self.x >= WIDTH or self.x < 0:
            self.dx *= -1
            self.x += self.dx  # Bounce back
        self.screen.set_char(self.x, self.y, '@')


    def KeyPressed(self, key):
        if key == curses.KEY_UP and self.y > 0:
            self.y -= 1
        elif key == curses.KEY_DOWN and self.y < HEIGHT - 1:
            self.y += 1