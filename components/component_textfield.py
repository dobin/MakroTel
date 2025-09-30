from components.component import Component
from components.sequence import Sequence

from config import MODE
if MODE == "minitel":
    from terminals.minitel_constants import LEFT, RIGHT, CORRECTION
else:
    import curses
    LEFT = curses.KEY_LEFT
    RIGHT = curses.KEY_RIGHT
    CORRECTION = curses.KEY_BACKSPACE  # or 127 for DEL


ACCENT_ACUTE = ord('´')  # Dead key for acute accent
ACCENT_GRAVE = ord('`')  # Dead key for grave accent  
ACCENT_CIRCUMFLEX = ord('^')  # Dead key for circumflex
ACCENT_DIAERESIS = ord('¨')  # Dead key for diaeresis
ACCENT_CEDILLA = ord('¸')  # Dead key for cedilla

# Characters from Minitel handled by the text field
MINITEL_CHARACTERS = (
    'abcdefghijklmnopqrstuvwxyz' +
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
    ' *$!:;,?./&(-_)=+\'@#' +
    '0123456789'
)

# from: https://github.com/Zigazou/PyMinitel/blob/master/minitel/ui/ChampTexte.py
# Translated and adapted by Claude for this project


class ComponentTextField(Component):
    """Text field management class

    This class manages a text field. Like text fields in an HTML
    form, this text field has a displayable length and a
    maximum total length.

    TextField does not handle any label.

    The following attributes are available:

    - visible_length: length occupied by the field on screen
    - total_length: maximum number of characters in the field
    - value: field value (UTF-8 encoded)
    - cursor_x: cursor position in the field
    - offset: display start of the field on screen
    - accent: accent waiting to be applied to the next character
    - hidden_field: characters are not displayed on minitel, they are
                    replaced by '*' (used for passwords for example)
    """
    def __init__(self, framebuffer, x, y, visible_length,
                 total_length = None, value = '', color = None, hidden_field=False):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(visible_length, int)
        assert isinstance(total_length, int) or total_length == None
        assert isinstance(value, str)
        assert x + visible_length < 80
        assert visible_length >= 1
        if total_length == None:
            total_length = visible_length
        assert visible_length <= total_length

        super().__init__(framebuffer, x, y, 1, visible_length)

        # Initialize the field
        self.visible_length = visible_length
        self.total_length = total_length
        self.value = '' + value
        self.cursor_x = 0
        self.offset = 0
        self.activable = True
        self.accent = None
        self.hidden_field = hidden_field
        self.color = color

    def KeyPressed(self, keys: Sequence):
        """Key handling

        This method is automatically called by the main loop when a key is pressed.

        The keys handled by the TextField class are as follows:

        - LEFT, RIGHT, to move in the field,
        - CORRECTION (BACKSPACE), to delete the character to the left of the cursor,
        - ACCENT_ACUTE, ACCENT_GRAVE, ACCENT_CIRCUMFLEX, ACCENT_DIAERESIS,
        - ACCENT_CEDILLA,
        - ASCII characters that can be typed on a keyboard.

        :param keys:
            The key sequence received from the framebuffer.
        :type keys:
            a Sequence object
        """
        if keys.egale(LEFT):
            self.accent = None
            self.cursor_left()   
        elif keys.egale(RIGHT):
            self.accent = None
            self.cursor_right()        
        elif keys.egale(CORRECTION) or keys.egale(127):  # Backspace or DEL
            self.accent = None
            if self.cursor_left():
                self.value = (self.value[0:self.cursor_x] +
                               self.value[self.cursor_x + 1:])
                self.display()
        elif keys.egale(ACCENT_ACUTE) or keys.egale(ACCENT_GRAVE) or keys.egale(ACCENT_CIRCUMFLEX) or keys.egale(ACCENT_DIAERESIS):
            key = keys.valeurs[0] if keys.valeurs else 0
            self.accent = key
        elif keys.egale(ord('c')) and self.accent == ACCENT_CEDILLA:
            self.accent = None
            self.value = (self.value[0:self.cursor_x] +
                           'ç' +
                           self.value[self.cursor_x:])
            self.cursor_right()
            self.display()
        else:
            # Handle regular ASCII characters
            #             caractere = '' + chr(sequence.valeurs[0])
            key = keys.valeurs[0] if keys.valeurs else 0
            if 32 <= key <= 126 and chr(key) in MINITEL_CHARACTERS:
                character = chr(key)
                if self.accent is not None:
                    if character in 'aeiouAEIOU':
                        if self.accent == ACCENT_ACUTE:
                            character = 'áéíóúÁÉÍÓÚ'['aeiouAEIOU'.index(character)]
                        elif self.accent == ACCENT_GRAVE:
                            character = 'àèìòùÀÈÌÒÙ'['aeiouAEIOU'.index(character)]
                        elif self.accent == ACCENT_CIRCUMFLEX:
                            character = 'âêîôûÂÊÎÔÛ'['aeiouAEIOU'.index(character)]
                        elif self.accent == ACCENT_DIAERESIS:
                            character = 'äëïöüÄËÏÖÜ'['aeiouAEIOU'.index(character)]

                    self.accent = None

                self.value = (self.value[0:self.cursor_x] +
                               character +
                               self.value[self.cursor_x:])
                self.cursor_right()
                self.display()

    def cursor_left(self):
        """Move the cursor one character to the left

        If the cursor cannot be moved, a beep is emitted.

        If the cursor asks to move to a part of the field not yet
        visible, an offset occurs.

        :returns:
            True if the cursor has moved, False otherwise.
        """
        # We cannot move the cursor left if it is already on the first
        # character
        if self.cursor_x == 0:
            if hasattr(self.framebuffer, 'beep'):
                self.framebuffer.beep()
            return False

        self.cursor_x = self.cursor_x - 1

        # Perform an offset if the cursor overflows the visible area
        if self.cursor_x < self.offset:
            self.offset = max(
                0,
                int(self.offset - self.visible_length / 2)
            )
            self.display()

        return True
    
    def cursor_right(self):
        """Move the cursor one character to the right

        If the cursor cannot be moved, a beep is emitted.

        If the cursor asks to move to a part of the field not yet
        visible, an offset occurs.

        :returns:
            True if the cursor has moved, False otherwise.
        """
        # We cannot move the cursor right if it is already on the last
        # character or at max length
        if self.cursor_x == min(len(self.value), self.total_length):
            if hasattr(self.framebuffer, 'beep'):
                self.framebuffer.beep()
            return False
    
        self.cursor_x = self.cursor_x + 1

        # Perform an offset if the cursor overflows the visible area
        if self.cursor_x > self.offset + self.visible_length:
            self.offset = max(
                0,
                int(self.offset + self.visible_length / 2)
            )
            self.display()

        return True

    def handle_arrival(self):
        """Handle text field activation

        The method positions the cursor and makes it visible.
        """
        # TODO: Position cursor visually when framebuffer supports it
        pass

    def handle_departure(self):
        """Handle text field deactivation

        The method cancels any accent beginning and makes the cursor invisible.
        """
        self.accent = None
        # TODO: Hide cursor when framebuffer supports it

    def display(self):
        """Display the text field

        If the value is smaller than the displayed length, we fill the
        extra spaces with dots.

        After calling this method, the cursor is automatically positioned.

        This method is called whenever we want to display the element.
        """
        # Get a lock on the framebuffer for thread safety
        self.framebuffer.screen_lock.acquire()
        
        try:
            if not self.hidden_field:
                # If the field is not hidden, we display the characters
                val = str(self.value)
            else: 
                val = "*" * len(self.value) 

            if len(val) - self.offset <= self.visible_length:
                # Case value smaller than visible length
                display_text = val[self.offset:]
                display_text = display_text.ljust(self.visible_length, '.')
            else:
                # Case value larger than visible length
                display_text = val[
                    self.offset:
                    self.offset + self.visible_length
                ]

            # Display the content using framebuffer buffer
            for i, char in enumerate(display_text):
                if i < self.visible_length:
                    self.framebuffer.set_char(self.x + i, self.y, char)
                    
        finally:
            self.framebuffer.screen_lock.release()

    def Tick(self):
        """Update the text field display each tick"""
        self.display()
