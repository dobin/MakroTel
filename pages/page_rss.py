from pages.page import Page
from components.component_clock import ComponentClock
from components.component_label import ComponentLabel
from components.component_textarea import ComponentTextArea
from components.sequence import Sequence
from constants.keys import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from framebuffer import FrameBuffer
from config import HEIGHT
from mylogger import myLogger
import feedparser
import datetime
import time


# Mostly Claude generated

class PageRss(Page):
    def __init__(self, framebuffer: FrameBuffer):
        super().__init__(framebuffer)
        
        # Configuration
        self.feed_url = "https://feeds.bbci.co.uk/news/rss.xml"  # Default RSS feed
        self.entries_per_page = 4  # Fixed number of entries per page
        self.current_page = 0  # Current page index (0-based)
        self.total_pages = 0   # Total number of pages available
        
        # RSS data
        self.feed_data = None
        self.formatted_text = ""
        
        # Components
        # Line 0: Status bar with clock
        self.components.append(ComponentClock(framebuffer, 0, 0))
        
        # Line 1: Title
        self.title_label = ComponentLabel(framebuffer, 0, 0, self.framebuffer.width, "RSS News Feed", center=True)
        self.components.append(self.title_label)
        
        # Line 2: Pagination info and controls
        self.info_label = ComponentLabel(framebuffer, 0, HEIGHT-1, self.framebuffer.width, "Loading... (←→ to navigate)", center=True)
        self.components.append(self.info_label)
        
        # Line 3-24: RSS content text area (dynamic height based on entry count)
        self.calculate_textarea_height()
        self.textarea = ComponentTextArea(framebuffer, 0, 2, self.framebuffer.width, self.textarea_height, "Loading RSS feed...")
        self.components.append(self.textarea)
        
        # Load RSS feed
        self._load_rss_feed()
    
    def calculate_textarea_height(self):
        """Calculate textarea height based on number of entries and available space"""
        # We have HEIGHT (25) total lines
        # Line 0: clock / name, Line 1: info, Last line: footer
        self.textarea_height = HEIGHT - 3
    
    def _load_rss_feed(self):
        """Load and parse the RSS feed"""
        try:
            myLogger.log(f"Loading RSS feed from {self.feed_url}")
            self.feed_data = feedparser.parse(self.feed_url)
            
            if hasattr(self.feed_data, 'feed'):
                # Update title with feed name
                feed_title = str(getattr(self.feed_data.feed, 'title', 'RSS Feed'))[:30]  # Truncate if too long
                self.title_label.set_text(f"RSS: {feed_title}")
            
            self._format_entries()
            
        except Exception as e:
            error_msg = f"Error loading RSS feed: {str(e)}"
            myLogger.log(error_msg)
            self.formatted_text = error_msg
            if hasattr(self, 'textarea'):
                self.textarea.set_text(self.formatted_text)
    
    def _format_entries(self):
        """Format RSS entries for display"""
        if not self.feed_data or not self.feed_data.entries:
            self.formatted_text = "No RSS entries found."
            if hasattr(self, 'textarea'):
                self.textarea.set_text(self.formatted_text)
            return
        
        # Calculate pagination
        total_entries = len(self.feed_data.entries)
        self.total_pages = (total_entries + self.entries_per_page - 1) // self.entries_per_page
        
        # Ensure current page is valid
        if self.current_page >= self.total_pages:
            self.current_page = max(0, self.total_pages - 1)
        
        # Calculate entry range for current page
        start_idx = self.current_page * self.entries_per_page
        end_idx = min(start_idx + self.entries_per_page, total_entries)
        
        # Update info label with pagination info
        page_info = f"Page {self.current_page + 1}/{self.total_pages} (←→ navigate)"
        if hasattr(self, 'info_label'):
            self.info_label.set_text(page_info)
        
        formatted_lines = []
        
        for i in range(start_idx, end_idx):
            entry = self.feed_data.entries[i]
            entry_num = i + 1  # Global entry number
            
            # Format title (truncate if necessary)
            title = getattr(entry, 'title', 'No title')
            # Split long titles across multiple lines
            title_lines = self._wrap_text(title, self.framebuffer.width - 2)
            
            # Format date
            date_str = "No date"
            if hasattr(entry, 'published'):
                try:
                    # Parse the published date
                    published_parsed = getattr(entry, 'published_parsed', None)
                    if published_parsed:
                        published_time = time.mktime(published_parsed)
                        date_obj = datetime.datetime.fromtimestamp(published_time)
                        date_str = date_obj.strftime("%m/%d %H:%M")
                    else:
                        # Fallback to raw string if parsing fails
                        published_str = getattr(entry, 'published', '')
                        date_str = published_str[:16] if len(published_str) > 16 else published_str
                except:
                    date_str = "Date error"
            
            # Format entry number (show global entry number)
            formatted_lines.append(f"{entry_num}. Date: {date_str}")

            for line in title_lines:
                formatted_lines.append(f" {line}")
            formatted_lines.append("")  # Empty line between entries
        
        self.formatted_text = "\n".join(formatted_lines)
        
        if hasattr(self, 'textarea'):
            self.textarea.set_text(self.formatted_text)
    
    def _wrap_text(self, text, width):
        """Simple text wrapping function"""
        if len(text) <= width:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is longer than width, force break
                    lines.append(word[:width])
                    current_line = word[width:]
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def KeyPressed(self, keys: Sequence):
        """Handle key presses for RSS page"""
        # Handle pagination navigation
        if keys.egale(KEY_LEFT):
            if self.current_page > 0:
                self.current_page -= 1
                self._update_display()
        elif keys.egale(KEY_RIGHT):
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self._update_display()
        
        # Let parent handle other keys (like page switching)
        super().KeyPressed(keys)
        
        # Let textarea handle its own keys (up/down for scrolling)
        # This is handled automatically by the component system
    
    def _update_display(self):
        """Update the display when page changes"""
        # Reformat entries (this will update info label too)
        self._format_entries()
        
        myLogger.log(f"RSS display updated to show page {self.current_page + 1}/{self.total_pages}")