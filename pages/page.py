from components.sequence import Sequence
from framebuffer import FrameBuffer
from config import HEIGHT


class Page:
    def __init__(self, framebuffer: FrameBuffer):
        self.framebuffer = framebuffer


    def initial(self):
        pass


    def Tick(self):
        pass


    def KeyPressed(self, keys: Sequence):
        pass