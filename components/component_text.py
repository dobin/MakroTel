from components.component import Component


class ComponentText(Component):
    def __init__(self, terminal, x: int, y: int, text: str):
        super().__init__(terminal, x, y, 1, len(text))
        self.text = text


    def Initial(self):
        pass


    def Tick(self):
        self.terminal.screen_lock.acquire()
        for i, c in enumerate(self.text):
            self.terminal.set_char(self.x + i, self.y, c)
        self.terminal.screen_lock.release()
