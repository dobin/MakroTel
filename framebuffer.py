import threading
from terminals.minitel_model import *
from abc import ABC, abstractmethod

from constants.keys import MINITEL_COLOR, MINITEL_SIZE, LINE_HORIZONTAL_TOP, LINE_HORIZONTAL_CENTER, LINE_HORIZONTAL_BOTTOM, LINE_VERTICAL_LEFT, LINE_VERTICAL_CENTER, LINE_VERTICAL_RIGHT
from mylogger import myLogger
from config import *


INIT_CHAR = '\x01'

class CharacterAttributes:
    def __init__(self, char_color: MINITEL_COLOR = MINITEL_COLOR.WHITE, background_color: MINITEL_COLOR = MINITEL_COLOR.BLACK, size: MINITEL_SIZE = MINITEL_SIZE.NORMAL, underline: bool = False, blinking: bool = False, inverted: bool = False):
        self.char_color: MINITEL_COLOR = char_color
        self.background_color: MINITEL_COLOR = background_color
        self.size: MINITEL_SIZE = size
        self.underline: bool = underline
        self.blinking: bool = blinking
        self.inverted: bool = inverted

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


    def copy(self):
        """Create a deep copy of this CharacterAttributes object.
        
        Returns:
            CharacterAttributes: A new CharacterAttributes object with all the same values.
        """
        copied_attrs = CharacterAttributes(
            char_color=self.char_color,
            background_color=self.background_color,
            size=self.size,
            underline=self.underline,
            blinking=self.blinking,
            inverted=self.inverted
        )
        copied_attrs.z = self.z
        copied_attrs.order = self.order
        return copied_attrs


class BufferCharacter: 
    def __init__(self):
        self.char: str = INIT_CHAR
        self.attr: CharacterAttributes = CharacterAttributes()


    def Set(self, char: str, attr: CharacterAttributes):
        self.char = char
        self.attr = attr


    def __eq__(self, value: object) -> bool:
        if not isinstance(value, BufferCharacter):
            return NotImplemented
        return (self.char == value.char and
                self.attr == value.attr)


    def copy(self):
        """Create a deep copy of this BufferCharacter object.
        
        Returns:
            BufferCharacter: A new BufferCharacter object with copied char and attr.
        """
        copied_buffer_char = BufferCharacter()
        copied_buffer_char.char = self.char  # strings are immutable, so this is fine
        copied_buffer_char.attr = self.attr.copy()
        return copied_buffer_char


class Cell:
    def __init__(self, x, y):
        self.a_char: BufferCharacter = BufferCharacter()
        self.b_char: BufferCharacter = BufferCharacter()
        self.x = x
        self.y = y


    def copy(self):
        """Create a deep copy of this Cell object.
        
        Returns:
            Cell: A new Cell object with copied a_char, b_char BufferCharacters and x, y coordinates.
        """
        copied_cell = Cell(self.x, self.y)
        copied_cell.a_char = self.a_char.copy()
        copied_cell.b_char = self.b_char.copy()
        return copied_cell


class FrameBuffer():
    def __init__(self): 
        # 80 columns max, even if just 40 are used
        self.screen: list[list[Cell]] = [[Cell(x, y) for x in range(80)] for y in range(HEIGHT)]
        self.screen_lock = threading.Lock()
        self.draw_event = threading.Event()  # Event to signal when drawing is needed
        self.width = 40  # Default on Minitel1b init

    def set_width(self, width: int):
        self.width = width
    
    def set_char(self, x: int, y: int, char: str, attr: CharacterAttributes = CharacterAttributes()):
        if 0 <= x < self.width and 0 <= y < HEIGHT:
            self.screen[y][x].b_char.Set(char, attr=attr)


    # a and b
    def reset_buffer(self):
        for y in range(HEIGHT):
            for x in range(80):
                self.screen[y][x].a_char.Set(INIT_CHAR, attr=CharacterAttributes())
                self.screen[y][x].b_char.Set(INIT_CHAR, attr=CharacterAttributes())

    # only b
    def clear_buffer(self):
        for y in range(HEIGHT):
            for x in range(80):
                self.screen[y][x].b_char.Set(INIT_CHAR, attr=CharacterAttributes())


    def set_line(self, x: int, y: int, length: int, direction: str, attr: CharacterAttributes = CharacterAttributes(), align: int = 1):
        """Draw a line using appropriate ASCII/Minitel characters.
        
        Args:
            x: Starting X coordinate (0-based)
            y: Starting Y coordinate (0-based) 
            length: Length of the line in characters
            direction: "horizontal" or "vertical"
            attr: Character attributes for the line
            align: Alignment for horizontal lines (0: left, 1: center, 2: right)
        """
        if length <= 0:
            return
            
        if direction.lower() == "horizontal":
            # Use hyphen/dash for horizontal lines
            line_char = ''
            if align == 0:
                line_char = LINE_HORIZONTAL_TOP
            elif align == 1:
                line_char = LINE_HORIZONTAL_CENTER
            elif align == 2:
                line_char = LINE_HORIZONTAL_BOTTOM
            else:
                myLogger.log(f"Invalid align '{align}' in set_line. Use 0 (left), 1 (center), or 2 (right).")

            for i in range(length):
                if 0 <= x + i < self.width and 0 <= y < HEIGHT:
                    self.screen[y][x + i].b_char.Set(line_char, attr=attr)
                    
        elif direction.lower() == "vertical":
            line_char = ''
            if align == 0:
                line_char = LINE_VERTICAL_LEFT
            elif align == 1:
                line_char = LINE_VERTICAL_CENTER
            elif align == 2:
                line_char = LINE_VERTICAL_RIGHT
            else:
                myLogger.log(f"Invalid align '{align}' in set_line. Use 0 (top), 1 (center), or 2 (bottom).")
            for i in range(length):
                if 0 <= x < self.width and 0 <= y + i < HEIGHT:
                    self.screen[y + i][x].b_char.Set(line_char, attr=attr)
        else:
            myLogger.log(f"Invalid direction '{direction}' in set_line. Use 'horizontal' or 'vertical'.")

