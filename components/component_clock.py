
import time
from components.component import Component
from components.sequence import Sequence


class ComponentClock(Component):
    def __init__(self, terminal, x: int, y: int):
        super().__init__(terminal, x, y, 1, 8)


    def Initial(self):
        pass


    def Tick(self):
        t = time.localtime()
        timestr = time.strftime("%H:%M:%S", t)

        self.terminal.framebuffer.screen_lock.acquire()
        for i, c in enumerate(timestr):
            self.terminal.set_char(self.x + i, self.y, c)
        self.terminal.framebuffer.screen_lock.release()


    def KeyPressed(self, keys: Sequence):
        pass
