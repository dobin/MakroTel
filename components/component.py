

class Component:
    def __init__(self, terminal, x: int, y: int, h: int, w: int, bitmap=None):
        self.terminal = terminal
        self.x: int = x
        self.y: int = y
        self.h: int = h
        self.w: int = w
        self.bitmap = bitmap

    def Initial(self):
        pass

    def Tick(self):
        pass

    def KeyPressed(self, key: int):
        pass
