from terminals.minitel_constants import *
from terminals.video import VideoTerminal


def normalize_color(color):
    """Returns the Minitel color number.

    From a color provided as a string with the
    name of the color in French or an integer indicating a level of
    gray, this function returns the corresponding color number
    for the Minitel.

    :param color:
        Accepted values are black, red, green, yellow, blue,
        magenta, cyan, white, and integers from 0 (black) to 7 (white)
    :type color:
        a string or an integer

    :returns:
        The number of the corresponding color on the Minitel or None if
        the requested color is not valid.
    """
    assert isinstance(color, (str, int))

    # We convert the color to a string so that the caller
    # can use '0' (str) or 0 (int) interchangeably.
    color = str(color)

    if color in MINITEL_COLORS:
        return MINITEL_COLORS[color]

    return None


class VideoTeletel(VideoTerminal): 
    def __init__(self, terminal):
        self.terminal = terminal


    def color(self, character = None, background = None):
        """Defines the colors used for the next characters.

        The possible colors are black, red, green, yellow, blue, magenta,
        cyan, white and a gray level from 0 to 7.

        Note:
        In Videotex, the background color only applies to delimiters. These
        delimiters are the space and the semi-graphic characters. Defining
        the background color and immediately displaying a character other
        than a delimiter (a letter for example) will have no effect.

        If a color is set to None, the method does not send any
        command to the Minitel.

        If a color is not valid, it is simply ignored.

        :param character:
            color to assign to the foreground.
        :type character:
            a string, an integer or None

        :param background:
            color to assign to the background.
        :type background:
            a string, an integer or None
        """
        #assert isinstance(character, (str, int)) or character == None
        #assert isinstance(background, (str, int)) or background == None

        if character != None:
            self.terminal.send([ESC, 0x40 + character])
        if background != None:
            self.terminal.send([ESC, 0x50 + background])

    def position(self, column, row, relative = False):
        """Defines the position of the Minitel cursor

        Note:
        This method optimizes the cursor movement, so it is important
        to ask yourself about the positioning mode (relative vs.
        absolute) because the number of characters generated can range from 1 to 5.

        On the Minitel, the first column has the value 1. The first line
        also has the value 1 although line 0 exists. The latter
        corresponds to the status line and has a different operation
        from the other lines.

        :param column:
            column to position the cursor at
        :type column:
            a relative integer

        :param row:
            line to position the cursor at
        :type row:
            a relative integer

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
            # Absolute movement
            if column == 1 and row == 1:
                self.terminal.send([RS])
            else:
                self.terminal.send([US, 0x40 + row, 0x40 + column])
        else:
            # Relative movement from the current position
            if row != 0:
                if row >= -4 and row <= -1:
                    # Short movement up
                    self.terminal.send([VT]*-row)
                elif row >= 1 and row <= 4:
                    # Short movement down
                    self.terminal.send([LF]*row)
                else:
                    # Long movement up or down
                    direction = { True: 'B', False: 'A'}
                    self.terminal.send([CSI, str(row), direction[row < 0]])

            if column != 0:
                if column >= -4 and column <= -1:
                    # Short movement left
                    self.terminal.send([BS]*-column)
                elif column >= 1 and column <= 4:
                    # Short movement right
                    self.terminal.send([TAB]*column)
                else:
                    # Long movement left or right
                    direction = { True: 'C', False: 'D'}
                    self.terminal.send([CSI, str(column), direction[column < 0]])

    def size(self, width = 1, height = 1):
        """Defines the size of the next characters

        The Minitel is able to enlarge the characters. Four sizes are
        available:

        - width = 1, height = 1: normal size
        - width = 2, height = 1: characters twice as wide
        - width = 1, height = 2: characters twice as high
        - width = 2, height = 2: characters twice as high and wide

        Note:
        This command only works in Videotex mode.

        Positioning with characters twice as high is done from
        the bottom of the character.

        :param width:
            width multiplier (1 or 2)
        :type width:
            an integer

        :param height:
            height multiplier (1 or 2)
        :type height:
            an integer
        """
        assert width in [1, 2]
        assert height in [1, 2]

        self.terminal.send([ESC, 0x4c + (height - 1) + (width - 1) * 2])

    def effect(self, underline = None, blinking = None, inversion = None):
        """Activates or deactivates effects

        The Minitel has 3 effects on characters: underline,
        blinking and video inversion.

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

        # Manages underlining
        underlines = {True: [ESC, 0x5a], False: [ESC, 0x59], None: None}
        self.terminal.send(underlines[underline])

        # Manages blinking
        blinkings = {True: [ESC, 0x48], False: [ESC, 0x49], None: None}
        self.terminal.send(blinkings[blinking])

        # Manages video inversion
        inversions = {True: [ESC, 0x5d], False: [ESC, 0x5c], None: None}
        self.terminal.send(inversions[inversion])

    def clear(self, scope = 'all'):
        """Erases all or part of the screen

        This method allows to erase:


        :param scope:
            indicates the scope of the erasure:

            - the whole screen ('all'),
            - from the cursor to the end of the line ('endline'),
            - from the cursor to the bottom of the screen ('endscreen'),
            - from the beginning of the screen to the cursor ('startscreen'),
            - from the beginning of the line to the cursor ('start_line'),
            - the whole line ('line'),
            - the status line, row 00 ('status'),
            - the whole screen and the status line ('reallyall').
        :type porte:
            a string
        """
        scopes = {
            'all': [FF],
            'endline': [CAN],
            'endscreen': [CSI, 0x4a],
            'startscreen': [CSI, 0x31, 0x4a],
            #'all': [CSI, 0x32, 0x4a],
            'start_line': [CSI, 0x31, 0x4b],
            'line': [CSI, 0x32, 0x4b],
            'status': [US, 0x40, 0x41, CAN, LF],
            'reallyall': [FF, US, 0x40, 0x41, CAN, LF]
        }

        assert scope in scopes

        self.terminal.send(scopes[scope])

    def repeat(self, character, length):
        """Repeat a character

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
        assert isinstance(character, int) or len(character) == 1

        self.terminal.send([character, REP, 0x40 + length - 1])

    def beep(self):
        """Emits a beep

        Asks the Minitel to emit a beep
        """
        self.terminal.send([BEL])

    def line_start(self):
        """Return to the beginning of the line

        Positions the cursor at the beginning of the current line.
        """
        self.terminal.send([CR])

    def delete(self, nb_column = None, nb_row = None):
        """Deletes characters after the cursor

        By specifying a number of columns, this method deletes
        characters after the cursor, the Minitel brings back the last characters
        contained on the line.
        
        By specifying a number of lines, this method deletes lines
        below the line containing the cursor, moving up the following lines.

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
            self.terminal.send([CSI, str(nb_column), 'P'])

        if nb_row != None:
            self.terminal.send([CSI, str(nb_row), 'M'])    
            
    def insert(self, nb_column = None, nb_row = None):
        """Inserts characters after the cursor

        By inserting characters after the cursor, the Minitel pushes the
        last characters contained on the line to the right.

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
            self.terminal.send([CSI, '4h', ' ' * nb_column, CSI, '4l'])

        if nb_row != None:
            self.terminal.send([CSI, str(nb_row), 'L'])


    def cursor(self, visible):
        """Activates or deactivates the cursor display

        The Minitel can display a blinking cursor at the
        display position of the next characters.

        It is interesting to deactivate it when the computer has to send
        long character sequences because the Minitel will try to
        display the cursor for each character displayed, generating an
        unpleasant effect.

        :param visible:
            indicates whether to activate the cursor (True) or make it invisible
            (False)
        :type visible:
            a boolean
        """
        assert visible in [True, False]

        states = {True: CON, False: COF}
        self.terminal.send([states[visible]])


    def echo(self, active):
        """Activates or deactivates the keyboard echo

        By default, the Minitel sends any character typed on the keyboard to both
        the screen and the peripheral socket. This trick saves the
        computer from having to send the last typed character back to the screen,
        thus saving bandwidth.

        In the case where the computer offers a more advanced user interface,
        it is important to be able to control exactly what is
        displayed by the Minitel.

        The method returns True if the command has been correctly processed by the
        Minitel, False otherwise.

        :param active:
            indicates whether to activate the echo (True) or deactivate it (False)
        :type active:
            a boolean

        :returns:
            True if the command was accepted by the Minitel, False otherwise.
        """
        assert active in [True, False]

        actives = {
            True: [PRO3, ROUTING_ON, RECV_SCREEN, SEND_MODEM],
            False: [PRO3, ROUTING_OFF, RECV_SCREEN, SEND_MODEM]
        }
        response = self.terminal.call(actives[active], PRO3_LENGTH)
        
        return response.longueur == PRO3_LENGTH