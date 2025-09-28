

class Component:
    def __init__(self, screen, x, y, h, w, bitmap=None):
        self.screen = screen
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.bitmap = bitmap

    def Initial(self):
        pass

    def Tick(self):
        pass

    def KeyPressed(self, key):
        pass
