import threading
from terminals.minitel_model import *
from abc import ABC, abstractmethod

from constants.keys import MINITEL_COLOR, MINITEL_SIZE
from mylogger import myLogger
from config import *


class CharacterAttributes:
    def __init__(self, char_color: MINITEL_COLOR = MINITEL_COLOR.WHITE, background_color: MINITEL_COLOR = MINITEL_COLOR.BLACK, size: MINITEL_SIZE = MINITEL_SIZE.NORMAL, underline: bool = False, blinking: bool = False, inverted: bool = False):
        self.char_color: MINITEL_COLOR = char_color
        self.background_color: MINITEL_COLOR = background_color
        self.size: MINITEL_SIZE = size
        self.underline: bool = underline
        self.blinking: bool = blinking
        self.inverted: bool = False

        # MakroTel rendering specific
        self.z: int = 0
        self.order: int = 0


    def __eq__(self, value: object) -> bool:
        if not isinstance(value, CharacterAttributes):
            return NotImplemented
        return (self.char_color == value.char_color and
                self.background_color == value.background_color and
                self.size == value.size and
                self.underline == value.underline and
                self.blinking == value.blinking and
                self.inverted == value.inverted and
                self.z == value.z and
                self.order == value.order)


class BufferCharacter: 
    def __init__(self):
        self.char: str = ' '
        self.char_attributes: CharacterAttributes = CharacterAttributes()


    def Set(self, char: str, char_attributes: CharacterAttributes):
        self.char = char
        self.char_attributes = char_attributes


    def __eq__(self, value: object) -> bool:
        if not isinstance(value, BufferCharacter):
            return NotImplemented
        return (self.char == value.char and
                self.char_attributes == value.char_attributes)


class Cell:
    def __init__(self):
        self.a_char: BufferCharacter = BufferCharacter()
        self.b_char: BufferCharacter = BufferCharacter()


class FrameBuffer():
    def __init__(self): 
        self.screen: list[list[Cell]] = [[Cell() for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.screen_lock = threading.Lock()
        self.draw_event = threading.Event()  # Event to signal when drawing is needed


    def set_char(self, x: int, y: int, char: str, char_attributes: CharacterAttributes = CharacterAttributes()):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.screen[y][x].b_char.Set(char, char_attributes=char_attributes)


    def clear_buffer(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.screen[y][x].b_char.Set(CHAR_BG, char_attributes=CharacterAttributes())

