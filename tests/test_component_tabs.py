#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for ComponentTabs"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framebuffer import FrameBuffer
from components.component_tabs import ComponentTabs
from components.component_label import ComponentLabel


def test_component_tabs_basic():
    """Test basic tab functionality"""
    fb = FrameBuffer()
    tabs = ComponentTabs(fb, 0, 0, 80, 24)
    
    # Create some test components
    label1 = ComponentLabel(fb, 0, 0, 80, "Tab 1 Content")
    label2 = ComponentLabel(fb, 0, 0, 80, "Tab 2 Content")
    label3 = ComponentLabel(fb, 0, 0, 80, "Tab 3 Content")
    
    # Add tabs
    tabs.add_tab("tab1", label1)
    tabs.add_tab("tab2", label2)
    tabs.add_tab("tab3", label3)
    
    # First tab should be active by default
    assert tabs.get_active_tab() == "tab1"
    assert tabs.get_active_component() == label1
    
    # Switch tabs
    assert tabs.set_active_tab("tab2") == True
    assert tabs.get_active_tab() == "tab2"
    assert tabs.get_active_component() == label2
    
    # Try to switch to non-existent tab
    assert tabs.set_active_tab("tab999") == False
    assert tabs.get_active_tab() == "tab2"  # Should remain on tab2
    
    # Get tab names
    tab_names = tabs.get_tab_names()
    assert "tab1" in tab_names
    assert "tab2" in tab_names
    assert "tab3" in tab_names
    assert len(tab_names) == 3
    
    # Check tab existence
    assert tabs.has_tab("tab1") == True
    assert tabs.has_tab("tab999") == False
    
    print("✓ All ComponentTabs tests passed!")


def test_component_tabs_remove():
    """Test removing tabs"""
    fb = FrameBuffer()
    tabs = ComponentTabs(fb, 0, 0, 80, 24)
    
    label1 = ComponentLabel(fb, 0, 0, 80, "Tab 1")
    label2 = ComponentLabel(fb, 0, 0, 80, "Tab 2")
    
    tabs.add_tab("tab1", label1)
    tabs.add_tab("tab2", label2)
    
    assert tabs.get_active_tab() == "tab1"
    
    # Remove the active tab
    tabs.remove_tab("tab1")
    
    # Should switch to another tab (tab2)
    assert tabs.get_active_tab() == "tab2"
    assert len(tabs.get_tab_names()) == 1
    
    # Remove last tab
    tabs.remove_tab("tab2")
    assert tabs.get_active_tab() is None
    assert len(tabs.get_tab_names()) == 0
    
    print("✓ Remove tabs test passed!")


def test_component_tabs_clear():
    """Test clearing all tabs"""
    fb = FrameBuffer()
    tabs = ComponentTabs(fb, 0, 0, 80, 24)
    
    label1 = ComponentLabel(fb, 0, 0, 80, "Tab 1")
    label2 = ComponentLabel(fb, 0, 0, 80, "Tab 2")
    label3 = ComponentLabel(fb, 0, 0, 80, "Tab 3")
    
    tabs.add_tab("tab1", label1)
    tabs.add_tab("tab2", label2)
    tabs.add_tab("tab3", label3)
    
    assert len(tabs.get_tab_names()) == 3
    
    tabs.clear_tabs()
    
    assert len(tabs.get_tab_names()) == 0
    assert tabs.get_active_tab() is None
    
    print("✓ Clear tabs test passed!")


if __name__ == "__main__":
    test_component_tabs_basic()
    test_component_tabs_remove()
    test_component_tabs_clear()
    print("\n✅ All ComponentTabs tests passed successfully!")
