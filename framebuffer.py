import threading

from mylogger import myLogger
from config import *


class Cell:
    def __init__(self):
        # current, drawn
        self.a_char: str = ' '
        self.a_color = 0

        # new, to draw
        self.b_char: str = ' '
        self.b_color = 0
        self.b_type = 0


    def Set(self, char: str, color=0, type=0):
        self.b_char = char
        self.b_color = color
        self.b_type = type



class FrameBuffer():
    def __init__(self): 
        self.screen: list[list[Cell]] = [[Cell() for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.screen_lock = threading.Lock()
        self.draw_event = threading.Event()  # Event to signal when drawing is needed


    def set_char(self, x: int, y: int, char: str):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.screen[y][x].Set(char)


    def clear_buffer(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.screen[y][x].Set(CHAR_BG)

