from components.component import Component
from framebuffer import FrameBuffer, CharacterAttributes


# Similar to ComponentText but with width and optional centering
# One line only

class ComponentLabel(Component):
    def __init__(self, framebuffer, x: int, y: int, width: int, text: str, 
                 attributes: CharacterAttributes = CharacterAttributes(), 
                 center: bool = False):
        super().__init__(framebuffer, x, y, 1, width)
        self.text = text
        self.character_attributes = attributes
        self.center = center
        
        text_length = len(self.text)
        if text_length > self.w:
            # Truncate text if it's longer than width
            self.display_text = self.text[:self.w]
            self.start_x = self.x
        elif self.center:
            # Center the text
            padding = (self.w - text_length) // 2
            self.start_x = self.x + padding
            self.display_text = self.text
        else:
            # Left-align the text
            self.start_x = self.x
            self.display_text = self.text

    def Initial(self):
        self._draw_text()

    def Tick(self):
        self._draw_text()
        
    def _draw_text(self):
        self.framebuffer.screen_lock.acquire()
        
        # Draw the text using pre-calculated values
        for i, char in enumerate(self.display_text):
            if self.start_x + i < self.x + self.w:  # Ensure we don't exceed the width
                self.framebuffer.set_char(self.start_x + i, self.y, char, attr=self.character_attributes)
        
        self.framebuffer.screen_lock.release()

    def set_text(self, text):
        self.text = text
