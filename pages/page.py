from components.sequence import Sequence
from framebuffer import FrameBuffer
from config import HEIGHT


class Page:
    def __init__(self, framebuffer: FrameBuffer):
        self.framebuffer = framebuffer
        self.components: list = []
        self.x: int = 0
        self.y: int = HEIGHT // 2


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
