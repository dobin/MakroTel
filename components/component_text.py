from components.component import Component

from framebuffer import FrameBuffer, CharacterAttributes, CharacterAttributes


class ComponentText(Component):
    def __init__(self, framebuffer, x: int, y: int, text: str, attributes: CharacterAttributes = CharacterAttributes()):
        super().__init__(framebuffer, x, y, 1, len(text))
        self.text = text
        self.character_attributes = attributes


    def Initial(self):
        pass


    def Tick(self):
        self.framebuffer.screen_lock.acquire()

        for i, char in enumerate(self.text):
            self.framebuffer.set_char(self.x + i, self.y, char, char_attributes=self.character_attributes)
        self.framebuffer.screen_lock.release()
