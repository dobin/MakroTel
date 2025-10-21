import feedparser
import datetime
import time
import re
from typing import List

from pages.page import Page
from components.component_clock import ComponentClock
from components.component_label import ComponentLabel
from components.component_pageable_textarea import ComponentTextAreaPageable
from components.sequence import Sequence
from constants.keys import KEY_LEFT, KEY_RIGHT
from framebuffer import FrameBuffer
from config import HEIGHT
from mylogger import myLogger
from utils import parse_selection_key


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
        
        # RSS data
        self.feed_title = ""
        self.feed_entries: List[RssEntry] = []

        # Components
        # Line 1: Title
        self.c_title = ComponentLabel(framebuffer, 0, 0, self.framebuffer.width, "RSS News Feed", center=True)
        # Line 3-25: Pageable RSS content text area (includes info label on last line)
        self.pageable_textarea = ComponentTextAreaPageable(
            framebuffer, 
            0, 
            2, 
            self.framebuffer.width, 
            HEIGHT - 2,  # Takes lines 3-25 (height includes the info label)
            "",
            entries_per_page=self.entries_per_page
        )
        
        self.components.append(self.c_title)
        self.components.append(self.pageable_textarea)
        # Note: info_label is now part of pageable_textarea, no need to add separately


    def Initial(self):
        self._load_rss_feed()
        self._update_screen()
        

    def KeyPressed(self, keys: Sequence):
        """Handle key presses for RSS page"""
        # Left-right navigation is now handled by the pageable_textarea component
        
        if keys.egale(Sequence('r')):
            myLogger.log("PageRss: Reloading RSS feed")
            self._load_rss_feed()
            self._update_screen()
        else:
            # Number keys for selecting entries
            if keys.length() == 1:
                rel_id = parse_selection_key(keys.valeurs[0])
                if rel_id is not None and rel_id <= self.entries_per_page:
                    abs_id = self.pageable_textarea.rel_page_offset_to_abs_id(rel_id, len(self.feed_entries))
                    if abs_id != -1 and abs_id < len(self.feed_entries):
                        entry = self.feed_entries[abs_id]
                        myLogger.log(f"Selected Entry {entry.id}: {entry.title}")
                        pageReadInput = {
                            "id": entry.id,
                            "title": entry.title,
                            "content": entry.text,
                        }
                        if self.pageManager is not None:
                            self.pageManager.set_current_page("80Read", pageReadInput)
        
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
        """Update the screen with current RSS feed content"""
        self.c_title.set_text(self.feed_title)

        # Calculate pagination
        total_entries = len(self.feed_entries)
        
        # Generate all pages
        all_pages = []
        total_pages = max(1, (total_entries + self.entries_per_page - 1) // self.entries_per_page)
        
        for page_num in range(total_pages):
            # Calculate entry range for this page
            start_idx = page_num * self.entries_per_page
            end_idx = min(start_idx + self.entries_per_page, total_entries)
            
            # Format the entries for this page
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
            all_pages.append(formatted_text)
        
        # Update the pageable textarea with all page contents
        self.pageable_textarea.set_page_contents(all_pages)
    
    
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
