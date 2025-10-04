
import time
from components.component import Component
from components.sequence import Sequence


class ComponentClock(Component):
    def __init__(self, framebuffer, x: int, y: int):
        super().__init__(framebuffer, x, y, 1, 8)


    def Initial(self):
        self._draw_clock()


    def Tick(self):
        self._draw_clock()


    def _draw_clock(self):
        t = time.localtime()
        timestr = time.strftime("%H:%M:%S", t)
        self.framebuffer.screen_lock.acquire()
        for i, c in enumerate(timestr):
            self.framebuffer.set_char(self.x + i, self.y, c)
        self.framebuffer.screen_lock.release()


    def KeyPressed(self, keys: Sequence):
        pass
