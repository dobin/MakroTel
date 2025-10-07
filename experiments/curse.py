from constants.keys import MINITEL_COLOR
import curses
from mylogger import myLogger

stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()

color_pairs = {}
pair_number = 1
colors = [MINITEL_COLOR.WHITE, MINITEL_COLOR.GREY_1, MINITEL_COLOR.GREY_2, MINITEL_COLOR.GREY_3, MINITEL_COLOR.GREY_4, MINITEL_COLOR.GREY_5, MINITEL_COLOR.GREY_6, MINITEL_COLOR.BLACK]
curses_colors = [curses.COLOR_WHITE, 240, 242, 244, 246, 248, 250, curses.COLOR_BLACK]

for idx_fg, fg in enumerate(colors):
    for idx_bg, bg in enumerate(colors):
        curses.init_pair(pair_number, curses_colors[idx_fg], curses_colors[idx_bg])
        color_pairs[(fg, bg)] = pair_number
        myLogger.log(f"Initialized color pair {pair_number} for fg={fg} bg={bg}")
        pair_number += 1


if True:
    n = 0
    while n < pair_number - 1:
        stdscr.addstr(n, 0, f"Color pair {n}", curses.color_pair(n))
        stdscr.refresh()
        n += 1
else:
    n = 2
    color_idx = color_pairs[(MINITEL_COLOR.GREY_1, MINITEL_COLOR.BLACK)]
    stdscr.addstr(n, 0, f"Color pair {n}", curses.color_pair(color_idx))

    n = 4
    color_idx = color_pairs[(MINITEL_COLOR.GREY_4, MINITEL_COLOR.GREY_1)]
    stdscr.addstr(n, 0, f"Color pair {n}", curses.color_pair(color_idx))

stdscr.getch()

curses.endwin()
