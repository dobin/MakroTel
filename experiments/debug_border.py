#!/usr/bin/env python3
"""
Debug version of border window to identify the issue.
"""

import curses
import sys


def main(stdscr):
    """Debug version to see what's happening."""
    try:
        # Clear screen
        stdscr.clear()
        curses.curs_set(0)
        
        # Get and display screen dimensions first
        height, width = stdscr.getmaxyx()
        
        # Add some basic text to see if anything shows up
        stdscr.addstr(0, 0, f"Terminal size: {height} x {width}")
        stdscr.addstr(1, 0, "Testing basic text display...")
        stdscr.addstr(2, 0, "Press any key to continue to border test...")
        stdscr.refresh()
        stdscr.getch()
        
        # Clear and try a simple border
        stdscr.clear()
        
        # Create a very simple window
        if height > 10 and width > 20:
            win_height = 10
            win_width = 30
            start_y = 2
            start_x = 2
            
            stdscr.addstr(0, 0, f"Creating window: {win_height}x{win_width} at ({start_y},{start_x})")
            stdscr.refresh()
            
            # Create window
            win = curses.newwin(win_height, win_width, start_y, start_x)
            
            # Try to add border
            win.border()
            
            # Add simple content
            win.addstr(1, 1, "BORDER TEST")
            win.addstr(2, 1, "Can you see this?")
            win.addstr(3, 1, "Height: " + str(win_height))
            win.addstr(4, 1, "Width: " + str(win_width))
            win.addstr(6, 1, "Press any key...")
            
            # Refresh both windows
            stdscr.refresh()
            win.refresh()
            
        else:
            stdscr.addstr(3, 0, f"Terminal too small! Need at least 10x20, got {height}x{width}")
            stdscr.refresh()
        
        # Wait for input
        stdscr.getch()
        
    except Exception as e:
        # If there's an error, try to show it
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error: {str(e)}")
        stdscr.refresh()
        stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
        print("Debug completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()