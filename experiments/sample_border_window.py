#!/usr/bin/env python3
"""
Sample curses program that creates a window with a border.
This demonstrates basic curses functionality for creating bordered windows.
"""

import curses
import time


def main(stdscr):
    """Main function that sets up and displays a bordered window."""
    # Clear screen and hide cursor
    stdscr.clear()
    curses.curs_set(0)
    
    bordered_window_demo(stdscr)
    
    # Wait for user input without timeout first
    key = stdscr.getch()
    if key == ord('q') or key == ord('Q'):
        return
    
    create_custom_border_window(stdscr)


def bordered_window_demo(stdscr):
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Ensure we have minimum terminal size
    if height < 10 or width < 20:
        stdscr.addstr(0, 0, f"Terminal too small! Need at least 10x20, got {height}x{width}")
        stdscr.addstr(1, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
        return
    
    # Create a window with border (leaving some margin from screen edges)
    # Make sure dimensions are valid
    win_height = max(8, height - 4)
    win_width = max(20, width - 8)
    start_y = 2
    start_x = 4
    
    # Double-check that window fits in screen
    if start_y + win_height >= height or start_x + win_width >= width:
        win_height = height - 6
        win_width = width - 10
        start_y = 2
        start_x = 2
    
    # Show debug info on main screen first
    stdscr.addstr(0, 0, f"Terminal: {height}x{width}, Window: {win_height}x{win_width} at ({start_y},{start_x})")
    stdscr.addstr(1, 0, "Creating bordered window... Press any key after viewing")
    stdscr.refresh()
    
    # Create the window
    win = curses.newwin(win_height, win_width, start_y, start_x)
    
    # Draw border around the window
    win.border()
    
    # Add a title to the window
    title = " Bordered Window Sample "
    win.addstr(0, (win_width - len(title)) // 2, title)
    
    # Add some content inside the window
    content_lines = [
        "This is a sample curses window with a border.",
        "",
        "Window dimensions:",
        f"  Height: {win_height}",
        f"  Width: {win_width}",
        f"  Position: ({start_y}, {start_x})",
        "",
        "Border characters used:",
        "  Corners: + (automatically chosen by curses)",
        "  Horizontal: - (automatically chosen by curses)",
        "  Vertical: | (automatically chosen by curses)",
        "",
        "Press 'q' to quit, or any other key for custom border demo."
    ]
    
    # Add content to the window (starting from row 2 to avoid the border)
    for i, line in enumerate(content_lines):
        if i + 2 < win_height - 1:  # Make sure we don't write over the border
            win.addstr(i + 2, 2, line[:win_width - 4])  # Leave margin from borders
    
    # Refresh the window to display changes
    win.refresh()
    stdscr.refresh()


def create_custom_border_window(stdscr):
    """Alternative function showing custom border characters."""
    stdscr.clear()
    curses.curs_set(0)
    
    height, width = stdscr.getmaxyx()
    
    # Show transition message
    stdscr.addstr(0, 0, "Switching to custom border demo...")
    stdscr.addstr(1, 0, "Press any key to continue...")
    stdscr.refresh()
    stdscr.getch()
    
    # Clear screen for custom border demo
    stdscr.clear()
    
    # Create a smaller window for custom border demo
    win_height = min(15, height - 4)
    win_width = min(50, width - 4)
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2
    
    # Ensure the window fits
    if start_y < 0: start_y = 1
    if start_x < 0: start_x = 1
    if start_y + win_height >= height: win_height = height - start_y - 1
    if start_x + win_width >= width: win_width = width - start_x - 1
    
    win = curses.newwin(win_height, win_width, start_y, start_x)
    
    # Custom border with specific characters
    # border(ls, rs, ts, bs, tl, tr, bl, br)
    # ls=left side, rs=right side, ts=top side, bs=bottom side
    # tl=top-left, tr=top-right, bl=bottom-left, br=bottom-right
    win.border('|', '|', '-', '-', '+', '+', '+', '+')
    
    # Add title
    title = " Custom Border Style "
    win.addstr(0, (win_width - len(title)) // 2, title)
    
    # Add content
    win.addstr(2, 2, "This window uses custom border characters:")
    win.addstr(4, 2, "  Sides: | (vertical bars)")
    win.addstr(5, 2, "  Top/Bottom: - (hyphens)")
    win.addstr(6, 2, "  Corners: + (plus signs)")
    win.addstr(8, 2, "You can customize each border character")
    win.addstr(9, 2, "individually for different styles.")
    win.addstr(11, 2, "Press any key to exit demo...")
    
    # Refresh both screens
    stdscr.refresh()
    win.refresh()
    stdscr.getch()


if __name__ == "__main__":
    try:
        # Initialize curses
        curses.wrapper(main)
        print("Border window demo completed!")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Program finished.")