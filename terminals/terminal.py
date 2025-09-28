from config import *


class Cell:
    def __init__(self):
        # current, drawn
        self.a_char: str = ''
        self.a_color = 0

        # new, to draw
        self.b_char: str = ''
        self.b_color = 0
        self.b_type = 0


    def Set(self, char: str, color=0, type=0):
        self.b_char = char
        self.b_color = color
        self.b_type = type
        

class Terminal:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.width: int = WIDTH
        self.height: int = HEIGHT
        self.bg_char: str = CHAR_BG
        self.screen: list[list[Cell]] = [[Cell() for _ in range(self.width)] for _ in range(self.height)]


    def draw_buffer(self):
        pass


    def set_char(self, x: int, y: int, char: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen[y][x].Set(char)


    def clear_buffer(self):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x].Set(self.bg_char)
