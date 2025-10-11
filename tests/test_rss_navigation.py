#!/usr/bin/env python3
"""
Test script for PageRss key navigation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.page_rss import PageRss
from framebuffer import FrameBuffer
from components.sequence import Sequence
from constants.keys import KEY_LEFT, KEY_RIGHT
import time

def test_rss_navigation():
    """Test RSS page key navigation"""
    print("Testing RSS page key navigation...")
    
    # Create framebuffer and RSS page
    framebuffer = FrameBuffer()
    rss_page = PageRss(framebuffer)
    
    # Wait for RSS to load
    time.sleep(2)
    
    initial_page = rss_page.current_page
    total_pages = rss_page.total_pages
    
    print(f"Initial page: {initial_page + 1}/{total_pages}")
    
    # Test right key (next page)
    if total_pages > 1:
        print("Testing RIGHT key (next page)...")
        right_key = Sequence([KEY_RIGHT])
        rss_page.KeyPressed(right_key)
        
        if rss_page.current_page == initial_page + 1:
            print("✓ RIGHT key navigation works")
        else:
            print(f"⚠ RIGHT key failed: expected page {initial_page + 2}, got {rss_page.current_page + 1}")
        
        # Test left key (previous page)
        print("Testing LEFT key (previous page)...")
        left_key = Sequence([KEY_LEFT])
        rss_page.KeyPressed(left_key)
        
        if rss_page.current_page == initial_page:
            print("✓ LEFT key navigation works")
        else:
            print(f"⚠ LEFT key failed: expected page {initial_page + 1}, got {rss_page.current_page + 1}")
        
        # Test boundary conditions
        print("Testing boundary conditions...")
        
        # Go to first page
        rss_page.current_page = 0
        rss_page._update_display()
        rss_page.KeyPressed(left_key)  # Should stay at page 0
        
        if rss_page.current_page == 0:
            print("✓ LEFT key at first page works (stays at page 1)")
        else:
            print(f"⚠ LEFT key at first page failed: moved to page {rss_page.current_page + 1}")
        
        # Go to last page
        rss_page.current_page = total_pages - 1
        rss_page._update_display()
        rss_page.KeyPressed(right_key)  # Should stay at last page
        
        if rss_page.current_page == total_pages - 1:
            print(f"✓ RIGHT key at last page works (stays at page {total_pages})")
        else:
            print(f"⚠ RIGHT key at last page failed: moved to page {rss_page.current_page + 1}")
            
    else:
        print("⚠ Only one page available, cannot test navigation")
    
    print("\n✓ All navigation tests completed!")

if __name__ == "__main__":
    test_rss_navigation()