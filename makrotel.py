import curses
import time
import threading
import copy

# Screen dimensions
WIDTH = 40
HEIGHT = 4
CHAR_BG = "_"


class MyLogger:
    def __init__(self):
        self.file = open("makrotel.log", "a")

    def log(self, message):
        self.file.write(f"{time.ctime()}: {message}\n")
        self.file.flush()

logger = MyLogger()


class Cell:
    def __init__(self):
        # current, drawn
        self.a_char = ''
        self.a_color = 0

        # new, to draw
        self.b_char = ''
        self.b_color = 0
        self.b_type = 0


    def Set(self, char, color=0, type=0):
        self.b_char = char
        self.b_color = color
        self.b_type = type
        

class ScreenCurses:
    def __init__(self, stdscr):
        self.width = WIDTH
        self.height = HEIGHT
        self.bg_char = CHAR_BG
        self.screen = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.screen_lock = threading.Lock()

        self.stdscr = stdscr

        curses.curs_set(0)       # Hide cursor
        stdscr.nodelay(True)     # Non-blocking input
        stdscr.clear()


    def draw_buffer(self):
        n = 0

        # Stream current screen to the terminal
        # NOTE: We copy it for now
        # NOTE: Lock it so we have a clean copy
        self.screen_lock.acquire()
        screen_copy = copy.deepcopy(self.screen)
        self.screen_lock.release()
        for y, row in enumerate(screen_copy):
            for x, char in enumerate(row):
                if char.a_char != char.b_char:
                    # print
                    self.stdscr.addch(y, x, char.b_char)

                    # simulate slow drawing
                    time.sleep(0.02)

                    n += 1

        # NOTE: update the screen, indicate what we have written
        # NOTE: Lock probably not needed here
        self.screen_lock.acquire()
        for y, row in enumerate(screen_copy):
            for x, char in enumerate(row):
                self.screen[y][x].a_char = char.b_char
                self.screen[y][x].a_color = char.b_color
        self.screen_lock.release()

        logger.log(f"Redrew {n} chars")
        self.stdscr.refresh()


    def set_char(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            #self.screen[y][x] = char
            self.screen[y][x].Set(char)


    def clear_buffer(self):
        for y in range(self.height):
            for x in range(self.width):
                #self.screen[y][x] = self.bg_char
                self.screen[y][x].Set(self.bg_char)


class Page:
    def __init__(self, screen):
        self.components = []
        self.x = 0
        self.y = HEIGHT // 2
        self.dx = 1
        self.screen = screen


    def initial(self):
        self.screen.clear_buffer()
        self.screen.set_char(self.x, self.y, '@')


    def tick(self):
        # make the operation atomic
        self.screen.screen_lock.acquire()

        self.screen.clear_buffer()
        self.screen.set_char(1, 1, self.x % 10 + ord('0'))
        self.screen.set_char(self.x, self.y, '@')

        self.screen.screen_lock.release()

        # Handle input
        key = self.screen.stdscr.getch()
        if key == ord('q'):
            return
        elif key == curses.KEY_UP and self.y > 0:
            self.y -= 1
        elif key == curses.KEY_DOWN and self.y < HEIGHT - 1:
            self.y += 1

        # Move sprite horizontally
        self.x += self.dx
        if self.x >= WIDTH or self.x < 0:
            self.dx *= -1
            self.x += self.dx  # Bounce back


def main(stdscr):
    screen = ScreenCurses(stdscr)

    def draw_loop():
        while True:
            screen.draw_buffer()
            time.sleep(0.1)
    threading.Thread(target=draw_loop, daemon=True).start()

    page = Page(screen)
    page.initial()

    while True:
        page.tick()
        time.sleep(0.20)


# Run curses application
curses.wrapper(main)
