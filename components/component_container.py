#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Container component for holding other components within a bounded area"""

from components.component import Component
from components.sequence import Sequence
from constants.keys import LINE_HORIZONTAL_TOP, LINE_HORIZONTAL_CENTER, LINE_HORIZONTAL_BOTTOM, LINE_VERTICAL_LEFT, LINE_VERTICAL_CENTER, LINE_VERTICAL_RIGHT
from framebuffer import CharacterAttributes
from typing import Optional


class ComponentContainer(Component):
    """Container component that can hold other components within a bounded area.
    
    This component provides:
    - A rectangular bounded area defined by x, y, width, and height
    - Optional border drawing around the container
    - Management of child components within the container bounds
    - Automatic clipping of child components to container boundaries
    - Coordinate translation for child components (container-relative coordinates)
    """
    
    def __init__(self, framebuffer, x: int, y: int, h: int, w: int, 
                 border: bool = True, border_attributes: Optional[CharacterAttributes] = None):
        """Initialize the container component.
        
        Args:
            framebuffer: The framebuffer to draw to
            x: X coordinate of the container's top-left corner
            y: Y coordinate of the container's top-left corner  
            h: Height of the container (including border if enabled)
            w: Width of the container (including border if enabled)
            border: Whether to draw a border around the container
            border_attributes: Attributes for the border (color, style, etc.)
        """
        super().__init__(framebuffer, x, y, h, w)
        self.border = border
        self.border_attributes = border_attributes or CharacterAttributes()
        self.child_components = []
        
        # Calculate the inner area (content area) dimensions
        if self.border:
            self.inner_x = self.x + 1
            self.inner_y = self.y + 1
            self.inner_w = max(0, self.w - 2)
            self.inner_h = max(0, self.h - 2)
        else:
            self.inner_x = self.x
            self.inner_y = self.y
            self.inner_w = self.w
            self.inner_h = self.h

    def add_component(self, component: Component, relative_x: int = 0, relative_y: int = 0):
        """Add a child component to this container.
        
        Args:
            component: The component to add as a child
            relative_x: X offset relative to the container's inner area
            relative_y: Y offset relative to the container's inner area
        """
        # Adjust component position to be relative to container's inner area
        component.x = self.inner_x + relative_x
        component.y = self.inner_y + relative_y
        
        # Set the container as the component's parent (if the component supports it)
        if hasattr(component, 'parent_container'):
            setattr(component, 'parent_container', self)
            
        self.child_components.append(component)

    def remove_component(self, component: Component):
        """Remove a child component from this container.
        
        Args:
            component: The component to remove
        """
        if component in self.child_components:
            self.child_components.remove(component)
            if hasattr(component, 'parent_container'):
                setattr(component, 'parent_container', None)

    def clear_components(self):
        """Remove all child components from this container."""
        for component in self.child_components:
            if hasattr(component, 'parent_container'):
                setattr(component, 'parent_container', None)
        self.child_components.clear()

    def is_point_inside(self, x: int, y: int) -> bool:
        """Check if a point is inside the container's inner area.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            bool: True if the point is inside the container's inner area
        """
        return (self.inner_x <= x < self.inner_x + self.inner_w and
                self.inner_y <= y < self.inner_y + self.inner_h)

    def Initial(self):
        """Initialize the container and all its child components."""
        # Initialize all child components
        for component in self.child_components:
            component.Initial()
        self._draw_container()

    def Tick(self):
        """Update the container display and all child components each tick."""
        self._draw_container()
        
    
    def _draw_container(self):
        # Draw the container (border if enabled)
        if self.border:
            self._draw_border()
        
        # Update all child components
        # Note: We don't call framebuffer.screen_lock.acquire() in child components
        # since we already have the lock here
        for component in self.child_components:
            component.Tick()
                

    def KeyPressed(self, keys: Sequence):
        """Handle key press events and forward to child components.
        
        Args:
            keys: The key sequence that was pressed
        """
        # Forward key events to all child components
        # Components should handle their own focus/selection logic
        for component in self.child_components:
            component.KeyPressed(keys)

    def _draw_border(self):
        """Internal method to draw the border around the container."""
        self.framebuffer.screen_lock.acquire()
        
        if self.w < 2 or self.h < 2:
            return  # Too small to draw a border
            
        # Draw top border
        for i in range(self.w):
            char = LINE_HORIZONTAL_BOTTOM
            self.framebuffer.set_char(self.x + i, self.y, char, self.border_attributes)

        # Draw bottom border  
        for i in range(self.w):
            char = LINE_HORIZONTAL_TOP
            self.framebuffer.set_char(self.x + i, self.y + self.h - 1, char, self.border_attributes)

        # Draw left and right borders
        for i in range(1, self.h - 1):
            # Left border
            self.framebuffer.set_char(self.x, self.y + i, LINE_VERTICAL_LEFT, self.border_attributes)
            # Right border
            self.framebuffer.set_char(self.x + self.w - 1, self.y + i, LINE_VERTICAL_RIGHT, self.border_attributes)

        self.framebuffer.screen_lock.release()


    def set_page_manager(self, pageManager):
        """Set the page manager for this container and all child components.
        
        Args:
            pageManager: The page manager to set
        """
        super().set_page_manager(pageManager)
        # Propagate to child components
        for component in self.child_components:
            component.set_page_manager(pageManager)

    def get_child_components(self) -> list:
        """Get a list of all child components in this container.
        
        Returns:
            list: A copy of the child components list
        """
        return self.child_components.copy()

    def find_component_at(self, x: int, y: int) -> Optional[Component]:
        """Find the topmost child component at the given coordinates.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            Component: The component at the given coordinates, or None if none found
        """
        # Check from last added (topmost) to first added (bottommost)
        for component in reversed(self.child_components):
            if (component.x <= x < component.x + component.w and
                component.y <= y < component.y + component.h):
                return component
        return None