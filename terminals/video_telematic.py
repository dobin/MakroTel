from terminals.minitel_constants import *
from terminals.video import VideoTerminal
from mylogger import myLogger

class VideoTelematic(VideoTerminal): 
    def __init__(self, terminal):
        self.terminal = terminal


    def color(self, character = None, background = None):
        """Defines the colors used for the next characters.

        VT100 ANSI color sequences:
        - Foreground colors: 30-37 (black, red, green, yellow, blue, magenta, cyan, white)
        - Background colors: 40-47 (black, red, green, yellow, blue, magenta, cyan, white)

        :param character:
            color to assign to the foreground (0-7: black, red, green, yellow, blue, magenta, cyan, white)
        :type character:
            an integer or None

        :param background:
            color to assign to the background (0-7: black, red, green, yellow, blue, magenta, cyan, white)
        :type background:
            an integer or None
        """
        # VT100 ANSI color mapping
        color_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}  # Direct mapping for basic colors
        
        if character != None and character in color_map:
            # Send VT100 foreground color sequence: ESC[3<color>m
            color_code = 30 + color_map[character]
            self.terminal.send(f"\x1b[{color_code}m")
            
        if background != None and background in color_map:
            # Send VT100 background color sequence: ESC[4<color>m  
            color_code = 40 + color_map[background]
            self.terminal.send(f"\x1b[{color_code}m")

    def position(self, column, row, relative = False):
        """Defines the position of the cursor using VT100 sequences

        VT100 cursor positioning:
        - Absolute: ESC[<row>;<col>H (1-based coordinates)
        - Relative: ESC[<count>A (up), ESC[<count>B (down), ESC[<count>C (right), ESC[<count>D (left)

        :param column:
            column to position the cursor at
        :type column:
            an integer

        :param row:
            line to position the cursor at
        :type row:
            an integer

        :param relative:
            indicates whether the coordinates provided are relative
            (True) to the current cursor position or if
            they are absolute (False, default value)
        :type relative:
            a boolean
        """
        assert isinstance(column, int)
        assert isinstance(row, int)
        assert relative in [True, False]

        if not relative:
            # Absolute movement - VT100: ESC[<row>;<col>H
            if column == 1 and row == 1:
                self.terminal.send("\x1b[H")  # Home position
            else:
                self.terminal.send(f"\x1b[{row};{column}H")
        else:
            # Relative movement from the current position
            if row != 0:
                if row > 0:
                    # Move down: ESC[<count>B
                    self.terminal.send(f"\x1b[{row}B")
                else:
                    # Move up: ESC[<count>A
                    self.terminal.send(f"\x1b[{-row}A")

            if column != 0:
                if column > 0:
                    # Move right: ESC[<count>C
                    self.terminal.send(f"\x1b[{column}C")
                else:
                    # Move left: ESC[<count>D
                    self.terminal.send(f"\x1b[{-column}D")

    def size(self, width = 1, height = 1):
        """Defines the size of the next characters

        Note: VT100 terminals do not support character size modification.
        This function is left empty for compatibility.

        :param width:
            width multiplier (1 or 2) - ignored in VT100
        :type width:
            an integer

        :param height:
            height multiplier (1 or 2) - ignored in VT100
        :type height:
            an integer
        """
        # VT100 does not support character sizing - function left empty
        pass

    def effect(self, underline = None, blinking = None, inversion = None):
        """Activates or deactivates effects using VT100 SGR sequences

        VT100 text attributes:
        - Underline: ESC[4m (on), ESC[24m (off)
        - Blinking: ESC[5m (on), ESC[25m (off)
        - Video inversion (reverse): ESC[7m (on), ESC[27m (off)

        :param underline:
            indicates whether to activate underlining (True) or deactivate it
            (False)
        :type underline:
            a boolean or None

        :param blinking:
            indicates whether to activate blinking (True) or deactivate it
            (False)
        :type blinking:
            a boolean or None

        :param inversion:
            indicates whether to activate video inversion (True) or deactivate it
            (False)
        :type inversion:
            a boolean or None
        """
        assert underline in [True, False, None]
        assert blinking in [True, False, None]
        assert inversion in [True, False, None]

        # Manages underlining - VT100: ESC[4m (on), ESC[24m (off)
        if underline is True:
            self.terminal.send("\x1b[4m")
        elif underline is False:
            self.terminal.send("\x1b[24m")

        # Manages blinking - VT100: ESC[5m (on), ESC[25m (off)
        if blinking is True:
            self.terminal.send("\x1b[5m")
        elif blinking is False:
            self.terminal.send("\x1b[25m")

        # Manages video inversion - VT100: ESC[7m (on), ESC[27m (off)
        if inversion is True:
            self.terminal.send("\x1b[7m")
        elif inversion is False:
            self.terminal.send("\x1b[27m")

    def clear(self, scope = 'all'):
        """Erases all or part of the screen using VT100 erase sequences

        VT100 erase sequences:
        - ESC[2J: Clear entire screen
        - ESC[K or ESC[0K: Clear from cursor to end of line  
        - ESC[1K: Clear from beginning of line to cursor
        - ESC[2K: Clear entire line
        - ESC[J or ESC[0J: Clear from cursor to end of screen
        - ESC[1J: Clear from beginning of screen to cursor

        :param scope:
            indicates the scope of the erasure:

            - the whole screen ('all'),
            - from the cursor to the end of the line ('endline'),
            - from the cursor to the bottom of the screen ('endscreen'),
            - from the beginning of the screen to the cursor ('startscreen'),
            - from the beginning of the line to the cursor ('start_line'),
            - the whole line ('line'),
            - the status line, row 00 ('status') - not supported in VT100,
            - the whole screen and the status line ('reallyall').
        :type scope:
            a string
        """
        scopes = {
            'all': "\x1b[2J",              # Clear entire screen
            'endline': "\x1b[K",           # Clear from cursor to end of line
            'endscreen': "\x1b[J",         # Clear from cursor to end of screen  
            'startscreen': "\x1b[1J",      # Clear from beginning of screen to cursor
            'start_line': "\x1b[1K",       # Clear from beginning of line to cursor
            'line': "\x1b[2K",             # Clear entire line
            'status': "",                  # Status line not supported in VT100
            'reallyall': "\x1b[2J"         # Clear entire screen (same as 'all')
        }

        assert scope in scopes

        if scopes[scope]:  # Only send if sequence is not empty
            self.terminal.send(scopes[scope])

    def repeat(self, character, length):
        """Repeat a character

        VT100 does not have a native repeat command, so this is implemented
        by sending the character multiple times.

        :param character:
            character to repeat
        :type character:
            a string

        :param length:
            the number of times the character is repeated
        :type length:
            a positive integer
        """
        assert isinstance(length, int)
        assert length > 0 and length <= 40
        assert isinstance(character, (str, int, list))
        
        if isinstance(character, str):
            # Send the character repeated length times
            repeated_char = character * length
            self.terminal.send(repeated_char)
        elif isinstance(character, int):
            # Convert int to character and repeat
            repeated_char = chr(character) * length  
            self.terminal.send(repeated_char)
        elif isinstance(character, list):
            # Send the list repeated length times
            for _ in range(length):
                self.terminal.send(character)

    def beep(self):
        """Emits a beep

        VT100 uses the standard ASCII bell character (0x07)
        """
        self.terminal.send("\x07")  # ASCII BEL character

    def line_start(self):
        """Return to the beginning of the line

        Positions the cursor at the beginning of the current line using VT100.
        """
        self.terminal.send("\x0d")  # ASCII CR (Carriage Return)

    def delete(self, nb_column = None, nb_row = None):
        """Deletes characters after the cursor using VT100 sequences

        VT100 delete sequences:
        - ESC[<n>P: Delete n characters at cursor position
        - ESC[<n>M: Delete n lines at cursor position

        :param nb_column:
            number of characters to delete
        :type nb_column:
            a positive integer
        :param nb_row:
            number of lines to delete
        :type nb_row:
            a positive integer
        """
        assert (isinstance(nb_column, int) and nb_column >= 0) or \
                nb_column == None
        assert (isinstance(nb_row, int) and nb_row >= 0) or \
                 nb_row == None

        if nb_column != None:
            # VT100: ESC[<n>P - Delete n characters
            if nb_column == 1:
                self.terminal.send("\x1b[P")
            else:
                self.terminal.send(f"\x1b[{nb_column}P")

        if nb_row != None:
            # VT100: ESC[<n>M - Delete n lines
            if nb_row == 1:
                self.terminal.send("\x1b[M")
            else:
                self.terminal.send(f"\x1b[{nb_row}M")    
            
    def insert(self, nb_column = None, nb_row = None):
        """Inserts characters after the cursor using VT100 sequences

        VT100 insert sequences:
        - ESC[<n>@: Insert n blank characters at cursor position  
        - ESC[<n>L: Insert n blank lines at cursor position

        :param nb_column:
            number of characters to insert
        :type nb_column:
            a positive integer
        :param nb_row:
            number of lines to insert
        :type nb_row:
            a positive integer
        """
        assert (isinstance(nb_column, int) and nb_column >= 0) or \
                nb_column == None
        assert (isinstance(nb_row, int) and nb_row >= 0) or \
                 nb_row == None

        if nb_column != None:
            # VT100: ESC[<n>@ - Insert n blank characters
            if nb_column == 1:
                self.terminal.send("\x1b[@")
            else:
                self.terminal.send(f"\x1b[{nb_column}@")

        if nb_row != None:
            # VT100: ESC[<n>L - Insert n blank lines
            if nb_row == 1:
                self.terminal.send("\x1b[L")
            else:
                self.terminal.send(f"\x1b[{nb_row}L")


    def cursor(self, visible):
        """Activates or deactivates the cursor visibility using VT100 sequences

        VT100 cursor visibility:
        - ESC[?25h: Show cursor
        - ESC[?25l: Hide cursor

        :param visible:
            indicates whether to make the cursor visible (True) or invisible (False)
        :type visible:
            a boolean
        """
        assert visible in [True, False]

        states = {True: "\x1b[?25h", False: "\x1b[?25l"}
        self.terminal.send(states[visible])


    def echo(self, active):
        """Activates or deactivates the keyboard echo using VT100 sequences

        VT100 does not have a native echo control sequence.
        This function is left empty for compatibility.

        :param active:
            indicates whether to activate (True) or deactivate (False) the echo
        :type active:
            a boolean
        """
        # VT100 does not support echo control - function left empty
        pass
