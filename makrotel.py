import curses
import time
import threading

# Screen dimensions
WIDTH = 40
HEIGHT = 25
CHAR_BG = "_"


class ScreenCurses:
    def __init__(self, stdscr):
        self.width = WIDTH
        self.height = HEIGHT
        self.bg_char = CHAR_BG
        self.screen = [[self.bg_char for _ in range(self.width)] for _ in range(self.height)]
        self.stdscr = stdscr

        curses.curs_set(0)       # Hide cursor
        stdscr.nodelay(True)     # Non-blocking input
        stdscr.clear()


    def draw_buffer(self):
        for y, row in enumerate(self.screen):
            for x, char in enumerate(row):
                self.stdscr.addch(y, x, char)
        self.stdscr.refresh()


    def set_char(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.screen[y][x] = char


    def clear_buffer(self):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x] = self.bg_char



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
        #self.screen.draw_buffer()


    def tick(self):
        self.screen.clear_buffer()
        self.screen.set_char(self.x, self.y, '@')
        #self.screen.draw_buffer()

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

    # create thread which invokes screen.draw_buffer() every 0.1 second
    def draw_loop():
        while True:
            screen.draw_buffer()
            time.sleep(0.1)
    threading.Thread(target=draw_loop, daemon=True).start()

    page = Page(screen)
    page.initial()

    while True:
        page.tick()
        time.sleep(0.10)  # Frame rate ~10 FPS


# Run curses application
curses.wrapper(main)
