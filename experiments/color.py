import curses

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    if not curses.has_colors():
        stdscr.addstr("No colors supported!")
        stdscr.getch()
        return
    
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    
    stdscr.addstr(0, 0, "Red Text", curses.color_pair(2))
    stdscr.addstr(1, 0, "Green Text", curses.color_pair(1))
    
    stdscr.getch()

curses.wrapper(main)