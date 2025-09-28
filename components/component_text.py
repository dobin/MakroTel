from components.component import Component


class ComponentText(Component):
    def __init__(self, screen, x, y, text):
        super().__init__(screen, x, y, 1, len(text))
        self.text = text


    def Tick(self):
        self.screen.screen_lock.acquire()
        for i, c in enumerate(self.text):
            self.screen.set_char(self.x + i, self.y, c)
        self.screen.screen_lock.release()
