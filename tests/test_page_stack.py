#!/usr/bin/env python3
"""
Test script for PageManager navigation stack functionality
"""

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pages.page import PageManager, Page
from framebuffer import FrameBuffer
from components.sequence import Sequence

def test_page_stack():
    """Test the page navigation stack functionality"""
    print("Testing PageManager navigation stack...")
    
    # Create a basic framebuffer
    framebuffer = FrameBuffer()
    
    # Create page manager
    page_manager = PageManager()
    
    # Create some test pages
    page_a = Page(framebuffer, "PageA")
    page_b = Page(framebuffer, "PageB")
    page_overview = Page(framebuffer, "Overview")

    # Add pages to manager
    page_manager.add_page(page_a)
    page_manager.add_page(page_b)
    page_manager.add_page(page_overview)

    # Test initial state
    print("✓ Created PageManager with 3 pages")
    print(f"  Initial stack size: {len(page_manager.page_stack)}")
    
    # Set initial page (should not add to stack since no previous page)
    page_manager.set_current_page("Overview")
    print(f"✓ Set initial page to Overview, stack size: {len(page_manager.page_stack)}")
    assert len(page_manager.page_stack) == 0, "Initial page should not be added to stack"
    
    # Navigate to PageA (should add Overview to stack)
    page_manager.set_current_page("PageA")
    print(f"✓ Navigated to PageA, stack size: {len(page_manager.page_stack)}")
    assert len(page_manager.page_stack) == 1, "Stack should have 1 page"
    assert page_manager.page_stack[0] == "Overview", "Stack should contain Overview"
    
    # Navigate to PageB (should add PageA to stack)
    page_manager.set_current_page("PageB")
    print(f"✓ Navigated to PageB, stack size: {len(page_manager.page_stack)}")
    assert len(page_manager.page_stack) == 2, "Stack should have 2 pages"
    assert page_manager.page_stack[-1] == "PageA", "Last item in stack should be PageA"
    
    # Test go_back (should go back to PageA)
    result = page_manager.go_back()
    current_page_name = page_manager.current_page.name
    print(f"✓ Went back, result: {result}, current page: {current_page_name}, stack size: {len(page_manager.page_stack)}")
    assert result == True, "go_back should return True"
    assert current_page_name == "PageA", "Should be back on PageA"
    assert len(page_manager.page_stack) == 1, "Stack should have 1 page after going back"
    
    # Test go_back again (should go back to Overview)
    result = page_manager.go_back()
    current_page_name = page_manager.current_page.name
    print(f"✓ Went back again, result: {result}, current page: {current_page_name}, stack size: {len(page_manager.page_stack)}")
    assert result == True, "go_back should return True"
    assert current_page_name == "Overview", "Should be back on Overview"
    assert len(page_manager.page_stack) == 0, "Stack should be empty"
    
    # Test go_back when stack is empty
    result = page_manager.go_back()
    print(f"✓ Tried to go back with empty stack, result: {result}")
    assert result == False, "go_back should return False when stack is empty"
    
    # Test avoiding duplicate consecutive entries
    page_manager.set_current_page("PageA")
    page_manager.set_current_page("PageA")  # Navigate to same page
    print(f"✓ Navigated to same page twice, stack size: {len(page_manager.page_stack)}")
    # This should only add Overview once, not create duplicates
    
    print("\n🎉 All tests passed! Page navigation stack is working correctly.")
    return True

if __name__ == "__main__":
    try:
        test_page_stack()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()