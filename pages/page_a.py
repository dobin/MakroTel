
from constants.keys import MINITEL_COLOR
from pages.page import Page
from components.sequence import Sequence

from framebuffer import FrameBuffer, CharacterAttributes
from terminals.terminal_minitel import *

from components.component_clock import ComponentClock
from components.component_text import ComponentText
from components.component_mover import ComponentMover
from components.component_menu import ComponentMenu
from components.component_textfield import ComponentTextField


class PageA(Page):
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer)

        self.components.append(ComponentClock(framebuffer, 1, 1))
        self.components.append(ComponentText(framebuffer, 12, 1, "MakroTel"))
        self.components.append(ComponentMover(framebuffer, 1, 2))
        self.components.append(ComponentTextField(framebuffer, 15, 3, 20))
        self.components.append(ComponentMenu(framebuffer, ["Item 1", "Item 2", "Item 3"], 1, 4))

        # Color: Foreground and other char attributes
        self.components.append(ComponentText(framebuffer, 18, 6, "WHITE", CharacterAttributes(char_color=MINITEL_COLOR.WHITE)))
        self.components.append(ComponentText(framebuffer, 18, 7, "GREY_1", CharacterAttributes(char_color=MINITEL_COLOR.GREY_1)))
        self.components.append(ComponentText(framebuffer, 18, 8, "GREY_2", CharacterAttributes(char_color=MINITEL_COLOR.GREY_2)))
        self.components.append(ComponentText(framebuffer, 18, 9, "GREY_3", CharacterAttributes(char_color=MINITEL_COLOR.GREY_3)))
        self.components.append(ComponentText(framebuffer, 18, 10, "GREY_4", CharacterAttributes(char_color=MINITEL_COLOR.GREY_4)))
        self.components.append(ComponentText(framebuffer, 18, 11, "GREY_5", CharacterAttributes(char_color=MINITEL_COLOR.GREY_5)))
        self.components.append(ComponentText(framebuffer, 18, 12, "GREY_6", CharacterAttributes(char_color=MINITEL_COLOR.GREY_6)))
        self.components.append(ComponentText(framebuffer, 18, 13, "BLACK", CharacterAttributes(char_color=MINITEL_COLOR.BLACK)))
        self.components.append(ComponentText(framebuffer, 18, 15, "BLINK", CharacterAttributes(blinking=True)))
        self.components.append(ComponentText(framebuffer, 18, 16, "UNDERLINE", CharacterAttributes(underline=True)))
        self.components.append(ComponentText(framebuffer, 18, 17, "INVERTED", CharacterAttributes(inverted=True)))

        # Color: Background
        delimiters = " `{\\¦}^~/_|"
        self.components.append(ComponentText(framebuffer, 25, 6, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.WHITE)))
        self.components.append(ComponentText(framebuffer, 25, 7, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.GREY_1)))
        self.components.append(ComponentText(framebuffer, 25, 8, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.GREY_2)))
        self.components.append(ComponentText(framebuffer, 25, 9, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.GREY_3)))
        self.components.append(ComponentText(framebuffer, 25, 10, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.GREY_4)))
        self.components.append(ComponentText(framebuffer, 25, 11, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.GREY_5)))
        self.components.append(ComponentText(framebuffer, 25, 12, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.GREY_6)))
        self.components.append(ComponentText(framebuffer, 25, 13, delimiters, CharacterAttributes(background_color=MINITEL_COLOR.BLACK)))

        test_string = "` { \\ ¦ } ^ ~ / _"
        self.components.append(ComponentText(framebuffer, 15, 4, test_string, CharacterAttributes(background_color=MINITEL_COLOR.BLACK)))
