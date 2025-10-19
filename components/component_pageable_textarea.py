

from components.component_textarea import ComponentTextArea
from components.component_label import ComponentLabel
from components.sequence import Sequence
from constants.keys import KEY_LEFT, KEY_RIGHT


# Mostly Claude generated

class ComponentTextAreaPageable(ComponentTextArea):
    """A pageable textarea component with left-right navigation and page indicator.
    
    This component combines a ComponentTextArea with a ComponentLabel for displaying
    page navigation information. It handles LEFT/RIGHT arrow keys to navigate between
    pages horizontally, while the parent ComponentTextArea handles UP/DOWN for vertical
    scrolling within a page.
    
    Attributes:
        - current_page: The current page number (0-based)
        - total_pages: Total number of pages
        - entries_per_page: Number of entries to display per page (configurable)
        - info_label: ComponentLabel that displays pagination info
        - textarea: The internal ComponentTextArea for displaying content
    """
    
    def __init__(self, framebuffer, x, y, width, height, text='', color=None, 
                 entries_per_page=6, info_text="←→ to navigate"):
        """Initialize the pageable textarea component.
        
        Args:
            framebuffer: The framebuffer to draw to
            x: X position of the component
            y: Y position of the component
            width: Width of the component
            height: Total height including the info label (info label uses last line)
            text: Initial text content
            color: Optional color for the text
            entries_per_page: Number of entries to show per page (default: 6)
            info_text: Text to display in the info label (default: "←→ to navigate")
        """
        # Initialize parent with height-1 to reserve space for info label
        super().__init__(framebuffer, x, y, width, height - 1, text, color)
        
        # Pagination configuration
        self.entries_per_page = entries_per_page
        self.page_current_page = 0  # Use different name to avoid confusion with parent's current_page
        self.page_total_pages = 0
        self.info_text = info_text
        self.page_contents = []  # Array of page content strings
        
        # Create info label on the last line
        self.info_label = ComponentLabel(
            framebuffer, 
            x, 
            y + height - 1,  # Last line
            width, 
            info_text, 
            center=True
        )
        
        # Callback for when page changes (can be set by parent)
        self.on_page_change_callback = None
        
    def Initial(self):
        """Initialize both textarea and info label"""
        super().Initial()
        self.info_label.Initial()
        
    def Tick(self):
        """Update both textarea and info label"""
        super().Tick()
        self.info_label.Tick()
        
    def KeyPressed(self, keys: Sequence):
        """Handle key presses for horizontal page navigation.
        
        LEFT/RIGHT arrows: Navigate between pages horizontally
        UP/DOWN arrows: Handled by parent ComponentTextArea for vertical scrolling
        """
        if keys.egale(KEY_LEFT):
            if self.page_current_page > 0:
                self.page_current_page -= 1
                self._update_current_page_display()
                self._update_page_info()
                # Notify parent that page changed
                if self.on_page_change_callback:
                    self.on_page_change_callback(self.page_current_page)
        elif keys.egale(KEY_RIGHT):
            if self.page_current_page < self.page_total_pages - 1:
                self.page_current_page += 1
                self._update_current_page_display()
                self._update_page_info()
                # Notify parent that page changed
                if self.on_page_change_callback:
                    self.on_page_change_callback(self.page_current_page)
        else:
            # Let parent handle other keys (UP/DOWN for scrolling within page)
            super().KeyPressed(keys)
            
    def set_page_contents(self, page_contents_array: list):
        """Set all page contents at once.
        
        Args:
            page_contents_array: List of strings, one per page
        """
        self.page_contents = page_contents_array
        self.page_total_pages = max(1, len(page_contents_array))
        
        # Ensure current page is valid
        if self.page_current_page >= self.page_total_pages:
            self.page_current_page = max(0, self.page_total_pages - 1)
        
        # Display the current page
        self._update_current_page_display()
        self._update_page_info()
    
    def _update_current_page_display(self):
        """Update the textarea with the content of the current page"""
        if 0 <= self.page_current_page < len(self.page_contents):
            self.set_text(self.page_contents[self.page_current_page])
        else:
            self.set_text("")
        
    def set_current_page(self, page_num: int):
        """Set the current page number (0-based)"""
        if 0 <= page_num < self.page_total_pages:
            self.page_current_page = page_num
            self._update_page_info()
            
    def get_current_page(self) -> int:
        """Get the current page number (0-based)"""
        return self.page_current_page
    
    def get_total_pages(self) -> int:
        """Get the total number of pages"""
        return self.page_total_pages
        
    def _update_page_info(self):
        """Update the info label with current pagination information"""
        page_info = f"Page {self.page_current_page + 1}/{self.page_total_pages} ({self.info_text})"
        self.info_label.set_text(page_info)
        
    def set_on_page_change_callback(self, callback):
        """Set a callback function to be called when the page changes.
        
        The callback will receive the new page number (0-based) as an argument.
        """
        self.on_page_change_callback = callback
