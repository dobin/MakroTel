#!/usr/bin/env python3
"""
Simple curses program that creates a window with a border.
This version is more robust and ensures the window is visible.
"""

import curses


def main(stdscr):
    """Main function that sets up and displays a bordered window."""
    # Initialize colors if available
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    # Clear screen and hide cursor
    stdscr.clear()
    curses.curs_set(0)
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Create a window that's easier to see
    win_height = min(20, height - 2)  # Limit height to 20 or screen height - 2
    win_width = min(60, width - 2)    # Limit width to 60 or screen width - 2
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2
    
    # Create the main window
    win = curses.newwin(win_height, win_width, start_y, start_x)
    
    # Set background color if colors are available
    if curses.has_colors():
        win.bkgd(' ', curses.color_pair(1))
    
    # Draw border around the window
    win.border()
    
    # Add a title to the window
    title = " BORDERED WINDOW DEMO "
    title_x = max(1, (win_width - len(title)) // 2)
    if curses.has_colors():
        win.addstr(0, title_x, title, curses.color_pair(2) | curses.A_BOLD)
    else:
        win.addstr(0, title_x, title, curses.A_BOLD)
    
    # Add content inside the window
    content_y = 2
    win.addstr(content_y, 2, "This is a bordered window created with curses!", curses.A_BOLD)
    content_y += 2
    
    win.addstr(content_y, 2, f"Terminal size: {height} x {width}")
    content_y += 1
    win.addstr(content_y, 2, f"Window size: {win_height} x {win_width}")
    content_y += 1
    win.addstr(content_y, 2, f"Window position: ({start_y}, {start_x})")
    content_y += 2
    
    win.addstr(content_y, 2, "The border is drawn using win.border()")
    content_y += 1
    win.addstr(content_y, 2, "which uses default characters:")
    content_y += 1
    win.addstr(content_y, 4, "- Corners: automatic")
    content_y += 1
    win.addstr(content_y, 4, "- Sides: automatic")
    content_y += 2
    
    # Instructions
    win.addstr(win_height - 3, 2, "Press any key to exit...", curses.A_REVERSE)
    
    # Refresh both windows
    stdscr.refresh()
    win.refresh()
    
    # Wait for any key press (no timeout)
    stdscr.nodelay(False)  # Make sure we wait for input
    stdscr.getch()


if __name__ == "__main__":
    try:
        # Use curses wrapper for proper initialization and cleanup
        curses.wrapper(main)
        print("Border window demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()