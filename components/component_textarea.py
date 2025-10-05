from components.component import Component
from components.sequence import Sequence
from constants.keys import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import textwrap


# Mostly Claude generated

class ComponentTextArea(Component):
    """Text area management class

    This class manages a multi-line text area that can display text with
    word wrapping and pagination. It supports:
    - Display of text with or without newlines
    - Automatic word wrapping when text exceeds width
    - Pagination when text exceeds display area
    - Navigation between pages using UP/DOWN keys
    - Page indicator showing current page and total pages

    The following attributes are available:

    - width: width of the display area (number of characters)
    - height: height of the display area (number of lines)
    - text: the text content to display
    - lines: processed lines of text (after word wrapping)
    - current_page: current page number (0-based)
    - total_pages: total number of pages
    - lines_per_page: number of lines that fit per page
    """
    
    def __init__(self, framebuffer, x, y, width, height, text='', color=None):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert isinstance(text, str)
        assert x + width <= 80  # Assuming 80 character terminal width
        assert width >= 1
        assert height >= 1

        super().__init__(framebuffer, x, y, height, width)

        # Initialize the text area
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.activable = True
        
        # Pagination state
        self.current_page = 0
        self.total_pages = 0
        self.lines_per_page = height - 1  # Reserve one line for page indicator
        
        # Process the text into lines
        self.lines = []
        self._process_text()

    def set_text(self, text):
        """Set new text content and reprocess it"""
        self.text = text
        self.current_page = 0
        self._process_text()

    def _process_text(self):
        """Process the input text into wrapped lines"""
        self.lines = []
        
        if not self.text:
            self.total_pages = 1
            return
            
        # Split text by existing newlines first
        paragraphs = self.text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph:
                # Empty line (newline)
                self.lines.append('')
            else:
                # Word wrap the paragraph to fit the width
                wrapped = textwrap.fill(paragraph, width=self.width, 
                                      break_long_words=True, 
                                      break_on_hyphens=True)
                wrapped_lines = wrapped.split('\n')
                self.lines.extend(wrapped_lines)
        
        # Calculate total pages
        if self.lines_per_page > 0:
            self.total_pages = max(1, (len(self.lines) + self.lines_per_page - 1) // self.lines_per_page)
        else:
            self.total_pages = 1

    def Tick(self):
        """Update the text area display each tick"""
        self._draw_textarea()

    def Initial(self):
        """Initial display of the text area"""
        self._draw_textarea()

    def KeyPressed(self, keys: Sequence):
        """Key handling for pagination

        This method handles the following keys:
        - UP: previous page
        - DOWN: next page

        :param keys: The key sequence received from the framebuffer
        :type keys: a Sequence object
        """
        if keys.egale(KEY_UP):
            self._previous_page()
        elif keys.egale(KEY_DOWN):
            self._next_page()

    def _previous_page(self):
        """Go to the previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._draw_textarea()
        else:
            # Beep if already on first page
            if hasattr(self.framebuffer, 'beep'):
                self.framebuffer.beep()

    def _next_page(self):
        """Go to the next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._draw_textarea()
        else:
            # Beep if already on last page
            if hasattr(self.framebuffer, 'beep'):
                self.framebuffer.beep()

    def _get_current_page_lines(self):
        """Get the lines for the current page"""
        if not self.lines:
            return []
            
        start_line = self.current_page * self.lines_per_page
        end_line = start_line + self.lines_per_page
        return self.lines[start_line:end_line]

    def _draw_textarea(self):
        """Display the text area with current page content and page indicator"""
        # Get a lock on the framebuffer for thread safety
        self.framebuffer.screen_lock.acquire()
        
        try:
            # Clear the display area
            for row in range(self.height):
                for col in range(self.width):
                    self.framebuffer.set_char(self.x + col, self.y + row, ' ')
            
            # Get lines for current page
            page_lines = self._get_current_page_lines()
            
            # Display the text lines
            for i, line in enumerate(page_lines):
                if i < self.lines_per_page:  # Make sure we don't exceed display area
                    # Truncate line if it's longer than width (shouldn't happen with word wrap)
                    display_line = line[:self.width] if len(line) > self.width else line
                    
                    # Display each character
                    for j, char in enumerate(display_line):
                        if j < self.width:
                            self.framebuffer.set_char(self.x + j, self.y + i, char)
            
            # Display page indicator on the last line if there are multiple pages
            if self.total_pages > 1:
                indicator_line = self.height - 1
                page_indicator = f"Page {self.current_page + 1}/{self.total_pages}"
                
                # Center the page indicator
                indicator_x = max(0, (self.width - len(page_indicator)) // 2)
                
                for j, char in enumerate(page_indicator):
                    if indicator_x + j < self.width:
                        self.framebuffer.set_char(self.x + indicator_x + j, 
                                                self.y + indicator_line, char)
                
                # Add navigation hints if there's space
                if self.width >= 30:  # Only show hints if area is wide enough
                    if self.current_page > 0:
                        # Show "↑" or "UP" for previous page
                        hint = "↑"
                        self.framebuffer.set_char(self.x, self.y + indicator_line, hint)
                    
                    if self.current_page < self.total_pages - 1:
                        # Show "↓" or "DN" for next page  
                        hint = "↓"
                        self.framebuffer.set_char(self.x + self.width - 1, 
                                                self.y + indicator_line, hint)
                        
        finally:
            self.framebuffer.screen_lock.release()

    def handle_arrival(self):
        """Handle text area activation"""
        # Make sure we're displaying the current content
        self._draw_textarea()

    def handle_departure(self):
        """Handle text area deactivation"""
        # Nothing special needed for departure
        pass
