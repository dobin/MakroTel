import feedparser
import datetime
import time
import re
from typing import List

from pages.page import Page
from components.component_clock import ComponentClock
from components.component_label import ComponentLabel
from components.component_textarea import ComponentTextArea
from components.sequence import Sequence
from constants.keys import KEY_LEFT, KEY_RIGHT
from framebuffer import FrameBuffer
from config import HEIGHT
from mylogger import myLogger


class RssEntry():
    def __init__(self, id: int, date: str, title: str, text: str, link: str):
        self.id: int = id
        self.date: str = date
        self.title: str = title
        self.text: str = text
        self.link: str = link


# initially Claude generated

class PageRss(Page):
    def __init__(self, framebuffer: FrameBuffer, name: str, feed_url):
        super().__init__(framebuffer, name)

        # Configuration
        self.feed_url = feed_url
        self.entries_per_page = 6
        self.current_page = 0
        self.total_pages = 0
        
        # RSS data
        #self.feed_data = None
        self.feed_title = ""
        self.feed_entries: List[RssEntry] = []

        # Components
        # Line 1: Title
        self.c_title = ComponentLabel(framebuffer, 0, 0, self.framebuffer.width, "RSS News Feed", center=True)
        # Line 3-24: RSS content text area (dynamic height based on entry count)
        self.textarea = ComponentTextArea(framebuffer, 0, 2, self.framebuffer.width, HEIGHT - 3, "")
        # Line 25: Pagination info and controls
        self.info_label = ComponentLabel(framebuffer, 0, HEIGHT-1, self.framebuffer.width, "←→ to navigate", center=True)
        
        self.components.append(self.c_title)
        self.components.append(self.info_label)
        self.components.append(self.textarea)

        self._load_rss_feed()


    def Initial(self):
        self._update_screen()


    def KeyPressed(self, keys: Sequence):
        """Handle key presses for RSS page"""
        # Handle pagination navigation

        if keys.egale(KEY_LEFT):
            if self.current_page > 0:
                self.current_page -= 1
                self._update_screen()
        elif keys.egale(KEY_RIGHT):
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self._update_screen()
        elif keys.egale(Sequence('r')):
            self._load_rss_feed()
            self._update_screen()
        else:
            # Number keys
            if keys.length() == 1 and keys.valeurs[0] in range(ord('1'), ord('1') + self.entries_per_page):
                rel_id = keys.valeurs[0] - ord('0')  # Convert ASCII to int (1-based)
                abs_id = self._rel_page_offset_to_abs_id(rel_id)
                if abs_id != -1 and abs_id < len(self.feed_entries):
                    entry = self.feed_entries[abs_id]
                    myLogger.log(f"Selected Entry {entry.id}: {entry.title}")
                    pageReadInput = {
                        "id": entry.id,
                        "title": entry.title,
                        "content": entry.text,
                    }
                    self.pageManager.set_current_page("80Read", pageReadInput)
        
        # Let textarea handle its own keys (up/down for scrolling)
        # This is handled automatically by the component system

        # Let parent handle other keys (like page switching)
        super().KeyPressed(keys)


    def _load_rss_feed(self):
        """Load and parse the RSS feed"""
        try:
            myLogger.log(f"PageRss: Loading RSS feed from {self.feed_url}")
            self.feed_entries = []

            feed_data = feedparser.parse(self.feed_url)
            if hasattr(feed_data, 'feed'):
                # Update title with feed name
                feed_title = str(getattr(feed_data.feed, 'title', 'RSS Feed'))[:30]  # Truncate if too long
                self.feed_title = f"RSS: {feed_title}"

                for id, entry in enumerate(feed_data.entries):
                    title_str = str(entry.get('title', ''))
                    
                    # Extract HTML content from the content structure
                    content_str = ''
                    content_data = entry.get('content', [])
                    if isinstance(content_data, list) and len(content_data) > 0:
                        # Look for HTML content type
                        for content_item in content_data:
                            if isinstance(content_item, dict) and content_item.get('type') == 'text/html':
                                content_str = str(content_item.get('value', ''))
                                break
                        # If no HTML found, try the first content item
                        if not content_str and isinstance(content_data[0], dict):
                            content_str = str(content_data[0].get('value', ''))
                    elif isinstance(content_data, str):
                        # Fallback for simple string content
                        content_str = content_data
                    
                    # Also try 'summary' as fallback if content is empty
                    if not content_str:
                        content_str = str(entry.get('summary', ''))
                    
                    content_str = self._strip_html_tags(content_str)
                    link_str = str(entry.get('link', ''))
                                            
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

                    rssEntry = RssEntry(id, date_str, title_str, content_str, link_str)
                    self.feed_entries.append(rssEntry)
            
        except Exception as e:
            error_msg = f"Error loading RSS feed: {str(e)}"
            myLogger.log(error_msg)

    
    def _update_screen(self):
        self.c_title.set_text(self.feed_title)

        # Calculate pagination
        total_entries = len(self.feed_entries)
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
        
        page_rel_id = 1
        for i in range(start_idx, end_idx):
            entry = self.feed_entries[i]

            # wrap title into lines
            title_lines = self._wrap_text(entry.title, self.framebuffer.width - 2)
            
            # first
            formatted_lines.append(f"{page_rel_id} {title_lines[0]}")
            # remaining
            for line in title_lines[1:]:
                formatted_lines.append(f"  {line}")
            formatted_lines.append("")  # Empty line between entries

            page_rel_id += 1
        
        formatted_text = "\n".join(formatted_lines)
        if hasattr(self, 'textarea'):
            self.textarea.set_text(formatted_text)
    

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


    def _rel_page_offset_to_abs_id(self, rel_id: int) -> int:
        """Convert relative page entry ID to absolute entry ID"""
        abs_id = self.current_page * self.entries_per_page + (rel_id - 1)
        if 0 <= abs_id < len(self.feed_entries):
            return abs_id
        return -1
    

    def _strip_html_tags(self, html_content: str) -> str:
        """Remove HTML tags and decode common HTML entities"""
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode common HTML entities
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'")
        clean_text = clean_text.replace('&nbsp;', ' ')
        
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
