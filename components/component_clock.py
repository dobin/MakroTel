
import time
from components.component import Component


class ComponentClock(Component):
    def __init__(self, screen, x, y):
        super().__init__(screen, x, y, 1, 8)

    def Initial(self):
        pass

    def Tick(self):
        t = time.localtime()
        timestr = time.strftime("%H:%M:%S", t)

        self.screen.screen_lock.acquire()
        for i, c in enumerate(timestr):
            self.screen.set_char(self.x + i, self.y, c)
        self.screen.screen_lock.release()

    def KeyPressed(self, key):
        pass
