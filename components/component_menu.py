#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Menu management class"""

from components.component import Component
from components.sequence import Sequence

from config import MODE
if MODE == "minitel":
    from terminals.minitel_constants import UP, DOWN
    KEY_UP = UP
    KEY_DOWN = DOWN
else:
    import curses
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN

# From: https://github.com/Zigazou/PyMinitel/blob/master/minitel/ui/UI.py
# Translated and adapted by Claude for this project


class ComponentMenu(Component):
    """Menu management class

    This class displays a menu to the user so they can select an entry using the UP and DOWN keys.

    The handling of actions for validation or cancellation is the responsibility of the calling program.

    It sets the following attributes:

    - options: list containing the options (unicode strings),
    - selection: selected option (index in the options list),
    - line_width: line width determined from the longest line.

    The options are contained in a list like this::

        options = [
          u'New',
          u'Open',
          u'-',
          u'Save',
          u'Save as...',
          u'Restore',
          u'-',
          u'Preview',
          u'Print...',
          u'-',
          u'Close',
          u'Quit'
        ]

    A dash (-) indicates a separator.

    There cannot be two identical entries in the options list.

    """
    def __init__(self, terminal, options, posx, posy, selection=0):
        self.options = options
        self.selection = selection

        # Determine the width of the menu
        self.line_width = 0
        for option in self.options:
            self.line_width = max(self.line_width, len(option))

        # Determine the width and height of the menu display area
        width = self.line_width + 2
        height = len(self.options) + 2

        super().__init__(terminal, posx, posy, height, width)

    def Initial(self):
        """Initialize the menu component"""
        # Find the first non-separator option for initial selection
        for i, option in enumerate(self.options):
            if option != '-':
                self.selection = i
                break

    def Tick(self):
        """Update the menu display each tick"""
        self.terminal.framebuffer.screen_lock.acquire()
        try:
            # Draw the menu using the terminal's character-based system
            self._draw_menu()
        finally:
            self.terminal.framebuffer.screen_lock.release()

    def _draw_menu(self):
        """Internal method to draw the complete menu"""
        # Draw the top border
        for i in range(self.w):
            char = '_' if i > 0 and i < self.w - 1 else '+'
            self.terminal.set_char(self.x + i, self.y, char)

        # Draw the menu options
        for i, option in enumerate(self.options):
            y_pos = self.y + 1 + i
            
            # Draw left border
            self.terminal.set_char(self.x, y_pos, '|')
            
            # Draw the option content
            if option == '-':
                # Draw separator
                for j in range(1, self.w - 1):
                    self.terminal.set_char(self.x + j, y_pos, '-')
            else:
                # Draw regular option
                display_text = option.ljust(self.line_width)
                if i == self.selection:
                    # Highlight selected option with brackets
                    display_text = f">{display_text[:self.line_width-1]}<"
                else:
                    display_text = f" {display_text[:self.line_width-1]} "
                
                for j, char in enumerate(display_text):
                    if j < self.line_width:
                        self.terminal.set_char(self.x + 1 + j, y_pos, char)
            
            # Draw right border
            self.terminal.set_char(self.x + self.w - 1, y_pos, '|')

        # Draw the bottom border
        for i in range(self.w):
            char = '_' if i > 0 and i < self.w - 1 else '+'
            self.terminal.set_char(self.x + i, self.y + self.h - 1, char)

    def KeyPressed(self, keys: Sequence):
        """Handle key presses for menu navigation"""
        if keys.egale(KEY_UP):
            selection = self.previous_option(self.selection)
            if selection is not None:
                self.selection = selection
            # Could add beep here if selection is None

        elif keys.egale(KEY_DOWN):
            selection = self.next_option(self.selection)
            if selection is not None:
                self.selection = selection
            # Could add beep here if selection is None

    def next_option(self, number):
        """Determine the index of the next option

        Returns the index of the option following the one indicated by the argument number.

        :param number:
            index of the line to select in the options list
        :type number:
            a positive integer

        :returns:
            the index of the next option or None if it does not exist.
        """
        assert isinstance(number, int)
        assert number >= 0 and number < len(self.options)

        # Browse the options after the index number within the limits of the options list
        for i in range(number + 1, len(self.options)):
            # Separators are ignored
            if self.options[i] != '-':
                return i

        # No option was found after the one indicated in number
        return None
    
    def previous_option(self, number):
        """Determine the index of the previous option

        Returns the index of the option preceding the one indicated by the argument number.

        :param number:
            index of the line to select in the options list
        :type number:
            a positive integer

        :returns:
            the index of the previous option or None if it does not exist.
        """
        assert isinstance(number, int)
        assert number >= 0 and number < len(self.options)

        # Browse the options before the index number within the limits of the options list
        for i in range(number - 1, -1, -1):
            # Separators are ignored
            if self.options[i] != '-':
                return i

        # No option was found before the one indicated in number
        return None