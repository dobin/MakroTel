from components.sequence import Sequence
from pages.page import Page
from framebuffer import FrameBuffer, CharacterAttributes
from config import HEIGHT
from constants.keys import MINITEL_COLOR

from components.component_text import ComponentText
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField
from components.component_container import ComponentContainer
from components.component_textarea import ComponentTextArea


class PageOverview(Page):
    def __init__(self, framebuffer: FrameBuffer, name: str):
        super().__init__(framebuffer, name)
        
        # Create the page title
        self.components.append(ComponentText(framebuffer, 15, 2, "MakroTel", 
                                           CharacterAttributes(char_color=MINITEL_COLOR.WHITE)))
        self.components.append(ComponentText(framebuffer, 12, 3, "Page Overview", 
                                           CharacterAttributes(char_color=MINITEL_COLOR.GREY_3)))
        
        # Create numbered list of available pages
        self.components.append(ComponentText(framebuffer, 5, 6, "1. PageA - Demo Page A"))
        self.components.append(ComponentText(framebuffer, 5, 7, "2. PageB - Demo Page B"))
        self.components.append(ComponentText(framebuffer, 5, 8, "3. Meditations - Philosophy"))
        self.components.append(ComponentText(framebuffer, 5, 9, "4. RSS - News Feed"))
        self.components.append(ComponentText(framebuffer, 5, 10, "5. 80-Column - Text Reader"))
        
        # Instructions
        self.components.append(ComponentText(framebuffer, 5, 13, "Press a number (1-5) to navigate", 
                                           CharacterAttributes(char_color=MINITEL_COLOR.GREY_4)))
        self.components.append(ComponentText(framebuffer, 5, 14, "Press 'O' from any page to return here", 
                                           CharacterAttributes(char_color=MINITEL_COLOR.GREY_5)))

    def Initial(self):
        super().Initial()

    def KeyPressed(self, keys: Sequence):
        # Handle number key navigation
        if self.pageManager is not None:
            if keys.egale(Sequence([ord('1')])):
                self.pageManager.set_current_page("PageA")
            elif keys.egale(Sequence([ord('2')])):
                self.pageManager.set_current_page("PageB")
            elif keys.egale(Sequence([ord('3')])):
                self.pageManager.set_current_page("Meditations")
            elif keys.egale(Sequence([ord('4')])):
                self.pageManager.set_current_page("RSS")
            elif keys.egale(Sequence([ord('5')])):
                self.pageManager.set_current_page("80Read", {
                    "id": 0,
                    "title": "",
                    "content": "AAAA " * 8 + "BBBB " * 8,
                })
        
        # Call parent to handle other keys and components
        return super().KeyPressed(keys)
    