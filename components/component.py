

from components.sequence import Sequence


class Component:
    def __init__(self, framebuffer, x: int, y: int, h: int, w: int, bitmap=None):
        self.framebuffer = framebuffer
        self.x: int = x
        self.y: int = y
        self.h: int = h
        self.w: int = w
        self.bitmap = bitmap

    def Initial(self):
        pass

    def Tick(self):
        pass

    def KeyPressed(self, keys: Sequence):
        pass
