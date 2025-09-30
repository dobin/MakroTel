from components.component import Component


class ComponentText(Component):
    def __init__(self, framebuffer, x: int, y: int, text: str):
        super().__init__(framebuffer, x, y, 1, len(text))
        self.text = text


    def Initial(self):
        pass


    def Tick(self):
        self.framebuffer.screen_lock.acquire()
        for i, c in enumerate(self.text):
            self.framebuffer.set_char(self.x + i, self.y, c)
        self.framebuffer.screen_lock.release()
