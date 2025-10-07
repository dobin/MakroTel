#!/usr/bin/env python3
"""
Simple blessed program that creates a window with a border.
This version uses the blessed library for more modern terminal handling.
"""

from blessed import Terminal
import sys


def draw_border(term, x, y, width, height, color=None):
    """Draw a border using Unicode box drawing characters."""
    # Box drawing characters
    top_left = '┌'
    top_right = '┐'
    bottom_left = '└'
    bottom_right = '┘'
    horizontal = '─'
    vertical = '│'
    
    # Apply color if specified
    if color:
        top_left = color + top_left
        top_right = color + top_right
        bottom_left = color + bottom_left
        bottom_right = color + bottom_right
        horizontal = color + horizontal
        vertical = color + vertical
    
    lines = []
    
    # Top border
    lines.append(term.move_xy(x, y) + top_left + horizontal * (width - 2) + top_right)
    
    # Side borders
    for i in range(1, height - 1):
        lines.append(term.move_xy(x, y + i) + vertical)
        lines.append(term.move_xy(x + width - 1, y + i) + vertical)
    
    # Bottom border
    lines.append(term.move_xy(x, y + height - 1) + bottom_left + horizontal * (width - 2) + bottom_right)
    
    return ''.join(lines)


def main():
    """Main function that sets up and displays a bordered window."""
    term = Terminal()
    
    # Clear screen and hide cursor
    print(term.clear + term.hide_cursor, end='')
    
    try:
        # Get terminal dimensions
        height = term.height
        width = term.width
        
        # Create a window that's easier to see
        win_height = min(20, height - 2)
        win_width = min(60, width - 2)
        start_y = (height - win_height) // 2
        start_x = (width - win_width) // 2
        
        # Set background color for the window area
        background = term.on_blue
        reset = term.normal
        
        # Fill the window area with background color
        for i in range(win_height):
            print(term.move_xy(start_x, start_y + i) + background + ' ' * win_width + reset, end='')
        
        # Draw border around the window
        border_color = term.white + term.on_blue
        print(draw_border(term, start_x, start_y, win_width, win_height, border_color), end='')
        
        # Add a title to the window
        title = " BORDERED WINDOW DEMO "
        title_x = start_x + max(1, (win_width - len(title)) // 2)
        title_color = term.yellow + term.bold + term.on_blue
        print(term.move_xy(title_x, start_y) + title_color + title + reset, end='')
        
        # Add content inside the window
        content_color = term.white + term.on_blue
        content_y = start_y + 2
        
        print(term.move_xy(start_x + 2, content_y) + content_color + term.bold + 
              "This is a bordered window created with blessed!" + reset, end='')
        content_y += 2
        
        print(term.move_xy(start_x + 2, content_y) + content_color + 
              f"Terminal size: {height} x {width}" + reset, end='')
        content_y += 1
        
        print(term.move_xy(start_x + 2, content_y) + content_color + 
              f"Window size: {win_height} x {win_width}" + reset, end='')
        content_y += 1
        
        print(term.move_xy(start_x + 2, content_y) + content_color + 
              f"Window position: ({start_y}, {start_x})" + reset, end='')
        content_y += 2
        
        print(term.move_xy(start_x + 2, content_y) + content_color + 
              "The border is drawn using Unicode box characters:" + reset, end='')
        content_y += 1
        
        print(term.move_xy(start_x + 4, content_y) + content_color + 
              "- Corners: ┌ ┐ └ ┘" + reset, end='')
        content_y += 1
        
        print(term.move_xy(start_x + 4, content_y) + content_color + 
              "- Sides: ─ │" + reset, end='')
        content_y += 2
        
        # Instructions
        instruction_color = term.black + term.on_white
        print(term.move_xy(start_x + 2, start_y + win_height - 3) + instruction_color + 
              "Press any key to exit..." + reset, end='')
        
        # Flush output
        sys.stdout.flush()
        
        # Wait for any key press
        with term.cbreak():
            term.inkey()
            
    finally:
        # Restore cursor and clear screen
        print(term.show_cursor + term.clear, end='')


if __name__ == "__main__":
    try:
        main()
        print("Border window demo completed successfully!")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()