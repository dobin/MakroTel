

from config import HEIGHT
from terminals.terminal import Terminal


class Page:
    def __init__(self, terminal: Terminal):
        self.terminal = terminal


    def initial(self):
        pass


    def Tick(self):
        pass


    def KeyPressed(self, key: int):
        pass