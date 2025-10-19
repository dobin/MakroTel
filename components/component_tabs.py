#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tabs component for managing multiple components with tab-based switching"""

from components.component import Component
from components.sequence import Sequence
from typing import Optional, Dict


class ComponentTabs(Component):
    """Tabs component that manages multiple child components as tabs.
    
    This component provides:
    - Management of multiple child components as named tabs
    - Only one tab (component) is active and visible at a time
    - Simple show/hide functionality based on the active tab name
    - No visual tab bar or UI - purely functional tab management
    """
    
    def __init__(self, framebuffer, x: int, y: int, h: int, w: int):
        """Initialize the tabs component.
        
        Args:
            framebuffer: The framebuffer to draw to
            x: X coordinate of the tabs area
            y: Y coordinate of the tabs area
            h: Height of the tabs area
            w: Width of the tabs area
        """
        super().__init__(framebuffer, x, y, h, w)
        self.tabs: Dict[str, Component] = {}  # Map of tab name to component
        self.active_tab: Optional[str] = None  # Name of the currently active tab

    def add_tab(self, name: str, component: Component):
        """Add a component as a new tab.
        
        Args:
            name: Unique name for this tab
            component: The component to add as a tab
        """
        # Set component position to match the tabs area
        component.x = self.x
        component.y = self.y
        component.w = self.w
        component.h = self.h
        
        # Set the tabs component as the component's parent (if supported)
        if hasattr(component, 'parent_container'):
            setattr(component, 'parent_container', self)
            
        self.tabs[name] = component
        
        # If this is the first tab, make it active
        if self.active_tab is None:
            self.active_tab = name

    def remove_tab(self, name: str):
        """Remove a tab by name.
        
        Args:
            name: Name of the tab to remove
        """
        if name in self.tabs:
            component = self.tabs[name]
            if hasattr(component, 'parent_container'):
                setattr(component, 'parent_container', None)
            del self.tabs[name]
            
            # If we removed the active tab, switch to another tab
            if self.active_tab == name:
                if self.tabs:
                    # Switch to the first available tab
                    self.active_tab = next(iter(self.tabs.keys()))
                else:
                    self.active_tab = None

    def clear_tabs(self):
        """Remove all tabs."""
        for component in self.tabs.values():
            if hasattr(component, 'parent_container'):
                setattr(component, 'parent_container', None)
        self.tabs.clear()
        self.active_tab = None

    def set_active_tab(self, name: str):
        """Set the active tab by name.
        
        Args:
            name: Name of the tab to activate
            
        Returns:
            bool: True if the tab was activated, False if tab name not found
        """
        if name in self.tabs:
            self.active_tab = name
            return True
        return False

    def get_active_tab(self) -> Optional[str]:
        """Get the name of the currently active tab.
        
        Returns:
            str: Name of the active tab, or None if no tabs exist
        """
        return self.active_tab

    def get_active_component(self) -> Optional[Component]:
        """Get the currently active component.
        
        Returns:
            Component: The active component, or None if no tabs exist
        """
        if self.active_tab:
            return self.tabs.get(self.active_tab)
        return None

    def get_tab_names(self) -> list:
        """Get a list of all tab names.
        
        Returns:
            list: List of tab names
        """
        return list(self.tabs.keys())

    def has_tab(self, name: str) -> bool:
        """Check if a tab with the given name exists.
        
        Args:
            name: Name to check
            
        Returns:
            bool: True if the tab exists
        """
        return name in self.tabs

    def Initial(self):
        """Initialize the tabs component and all tab components."""
        # Initialize all tab components
        for component in self.tabs.values():
            component.Initial()

    def Tick(self):
        """Update the active tab component each tick."""
        # Only update and draw the active tab
        if self.active_tab and self.active_tab in self.tabs:
            active_component = self.tabs[self.active_tab]
            active_component.Tick()

    def KeyPressed(self, keys: Sequence):
        """Handle key press events and forward to the active tab component.
        
        Args:
            keys: The key sequence that was pressed
        """
        # Only forward key events to the active tab
        if self.active_tab and self.active_tab in self.tabs:
            active_component = self.tabs[self.active_tab]
            active_component.KeyPressed(keys)

    def set_page_manager(self, pageManager):
        """Set the page manager for this tabs component and all tab components.
        
        Args:
            pageManager: The page manager to set
        """
        super().set_page_manager(pageManager)
        # Propagate to all tab components
        for component in self.tabs.values():
            component.set_page_manager(pageManager)

    def get_tab_component(self, name: str) -> Optional[Component]:
        """Get a specific tab component by name.
        
        Args:
            name: Name of the tab
            
        Returns:
            Component: The component for the given tab, or None if not found
        """
        return self.tabs.get(name)
