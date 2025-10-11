#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enum


"""Unified key constants for all terminal types

This module provides a unified interface for key constants across different
terminal types (Minitel and Curses). Components should import keys from here
instead of directly from terminal-specific modules.
"""

from config import MODE

# Minitel colors actually (monochrome crt)
class MINITEL_COLOR(enum.Enum):
    BLACK = 0
    GREY_1 = 4
    GREY_2 = 1
    GREY_3 = 5
    GREY_4 = 2
    GREY_5 = 6
    GREY_6 = 3
    WHITE = 7


class MINITEL_SIZE(enum.Enum):
    NORMAL = 0
    DOUBLE_WIDTH = 1
    DOUBLE_HEIGHT = 2
    DOUBLE_SIZE = 3



if MODE == "minitel":
    from terminals.minitel_constants import (
        UP, DOWN, LEFT, RIGHT, 
        RETURN, ENTER, 
        BS, 
        SEND, CANCEL, GUIDE, SUMMARY, CORRECTION, NEXT,
        SHIFT_UP, SHIFT_DOWN, SHIFT_LEFT, SHIFT_RIGHT,
        CTRL_LEFT
    )
    
    # Map minitel constants to unified names
    KEY_UP = UP
    KEY_DOWN = DOWN 
    KEY_LEFT = LEFT
    KEY_RIGHT = RIGHT
    KEY_ENTER = RETURN  # Minitel uses RETURN for the main enter key
    KEY_BACKSPACE = BS
    KEY_CORRECTION = CORRECTION

    LINE_VERTICAL_LEFT = "\x7B"
    LINE_VERTICAL_CENTER = "\x7C"
    LINE_VERTICAL_RIGHT = "\x7D"

    LINE_HORIZONTAL_TOP = "\x7E"
    LINE_HORIZONTAL_CENTER = "\x60"
    LINE_HORIZONTAL_BOTTOM = "\x5F"


else:
    import curses
    
    # Map curses constants to unified names
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_LEFT = curses.KEY_LEFT
    KEY_RIGHT = curses.KEY_RIGHT
    KEY_ENTER = 10  # ASCII code for Enter
    KEY_BACKSPACE = curses.KEY_BACKSPACE
    KEY_CORRECTION = curses.KEY_BACKSPACE

    LINE_HORIZONTAL_TOP = '-'
    LINE_HORIZONTAL_CENTER = '-'
    LINE_HORIZONTAL_BOTTOM = '_'

    LINE_VERTICAL_LEFT = '|'
    LINE_VERTICAL_CENTER = '|'
    LINE_VERTICAL_RIGHT = '|'


# Export all unified key constants
__all__ = [
    'KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT',
    'KEY_ENTER', 'KEY_BACKSPACE', 'KEY_CORRECTION',
]