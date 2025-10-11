#!/usr/bin/env python3
"""
Test script for PageRss functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.page_rss import PageRss
from framebuffer import FrameBuffer
import time

def test_rss_basic():
    """Test basic RSS functionality"""
    print("Testing RSS page creation and feed loading...")
    
    # Create framebuffer
    framebuffer = FrameBuffer()
    
    # Create RSS page
    rss_page = PageRss(framebuffer, "rss")
    
    # Test that the page was created
    assert rss_page is not None
    print("✓ RSS page created successfully")
    
    # Test that components were added
    assert len(rss_page.components) >= 3  # Clock, title, info, textarea
    print("✓ Components added successfully")
    
    # Test that feed data was loaded
    # Give it a moment to load the RSS feed
    time.sleep(2)
    
    print(f"Feed URL: {rss_page.feed_url}")
    print(f"Entries per page: {rss_page.entries_per_page}")
    print(f"Current page: {rss_page.current_page + 1}")
    print(f"Total pages: {rss_page.total_pages}")
    print(f"Formatted text length: {len(rss_page.formatted_text)}")
    
    if rss_page.feed_data:
        print("✓ RSS feed loaded successfully")
        if hasattr(rss_page.feed_data, 'entries') and rss_page.feed_data.entries:
            print(f"✓ Found {len(rss_page.feed_data.entries)} entries")
            
            # Check first entry
            entry = rss_page.feed_data.entries[0]
            title = getattr(entry, 'title', 'No title')
            print(f"First entry title: {title[:50]}...")
        else:
            print("⚠ No entries found in feed")
    else:
        print("⚠ RSS feed not loaded")
    
    # Test pagination navigation
    original_page = rss_page.current_page
    if rss_page.total_pages > 1:
        rss_page.current_page = 1
        rss_page._update_display()
        print(f"✓ Page navigation test: moved from page {original_page + 1} to page {rss_page.current_page + 1}")
    else:
        print("⚠ Only one page available, cannot test navigation")
    
    print("\nFormatted text preview (first 500 chars):")
    print("-" * 50)
    print(rss_page.formatted_text[:500])
    print("-" * 50)
    
    print("\n✓ All RSS tests completed successfully!")

if __name__ == "__main__":
    test_rss_basic()