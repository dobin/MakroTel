
import time
from components.component import Component


class ComponentClock(Component):
    def __init__(self, terminal, x: int, y: int):
        super().__init__(terminal, x, y, 1, 8)


    def Initial(self):
        pass


    def Tick(self):
        t = time.localtime()
        timestr = time.strftime("%H:%M:%S", t)

        self.terminal.screen_lock.acquire()
        for i, c in enumerate(timestr):
            self.terminal.set_char(self.x + i, self.y, c)
        self.terminal.screen_lock.release()


    def KeyPressed(self, key: int):
        pass
