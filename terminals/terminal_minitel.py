#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Minitel is a module for controlling a Minitel from a Python script.
"""

from config import DEBUG
from serial import Serial      # Physical link with the Minitel
from threading import Thread   # Threads for sending/receiving
import threading
from queue import Queue, Empty # Character queues for sending/receiving
import copy
import time

from framebuffer import FrameBuffer, INIT_CHAR, Cell
from constants.keys import MINITEL_COLOR
from mylogger import myLogger
from terminals.terminal import Terminal
from typing import cast

# Based on: https://github.com/Zigazou/PyMinitel/blob/master/minitel/Minitel.py
# Translated and adapted by Claude for this project

MODE_DIRECT = True

from components.sequence import Sequence # Manages character sequences

from terminals.minitel_constants import *
from terminals.minitel_model import *
from terminals.video_teletel import *
from terminals.video_telematic import *


class Minitel(Terminal):
    """A class for controlling the Minitel via a serial port

    Introduction
    ============

    The Minitel class allows sending and receiving character sequences
    to and from a Minitel in a Python program.
    It works via a serial connection between the computer and the Minitel.

    By default, it uses /dev/ttyUSB0 as the device. Indeed, one of
    the easiest ways to connect a Minitel to a computer
    is to use a 5v USB-TTL cable (PL2303) because the
    Minitel's peripheral socket works in TTL (0v/5v) and not in RS232
    (-12v/12v). This type of cable embeds a component that is recognized
    automatically by Linux kernels and is assigned to /dev/ttyUSB*. Under
    Android, the Linux kernel does not have the driver as standard.

    As long as the selected device is a serial device, this
    class should not have any problem communicating with the Minitel.
    For example, it is quite possible to create a serial proxy by
    using an Arduino connected via USB to the computer and whose some
    pins would be connected to the Minitel.

    The Minitel class allows to determine the operating speed of the
    Minitel, to identify the model, to configure it and to send and receive
    character sequences.

    Given its operation in threads, the main program
    using this class does not have to worry about being available to receive
    the character sequences sent by the Minitel.

    Quick start
    ================

    The life cycle of a Minitel object consists of creation,
    determining the Minitel's speed, its capabilities, the use
    of the Minitel by the application and the release of resources::
        
        from minitel.Minitel import Minitel

        minitel = Minitel()

        minitel.deviner_vitesse()
        minitel.identifier()

        # ...
        # Use of the minitel object
        # ...

        minitel.close()

    """
    def __init__(self, framebuffer: FrameBuffer, device = '/dev/ttyUSB0'):
        """Minitel constructor

        The serial connection is established according to the Minitel's basic standard.
        When switched on, the Minitel is configured at 1200 bps, 7 bits, even parity,
        Videotex mode.

        This may not correspond to the actual configuration of the Minitel at
        the time of execution. However, this is not a problem because the
        serial connection can be reconfigured at any time.

        :param device:
            The device to which the Minitel is connected. By default, the
            device is /dev/ttyUSB0
        :type device:
            String
    
        """
        assert isinstance(device, str)

        super().__init__(framebuffer)

        # Initializes the Minitel's state
        self.mode: MinitelVideoMode = MinitelVideoMode.VIDEOTEX
        self.speed = 1200

        # Initializes the list of Minitel capabilities
        self.capabilities = BASIC_CAPABILITIES

        # Connection status tracking
        self.is_connected = False
        self.connection_lock = threading.Lock()

        # Creates the two input/output queues
        self.input_queue = Queue()
        self.output_queue = Queue()

        # Initializes the connection with the Minitel
        self._minitel = Serial(
            device,
            baudrate = 1200, # 1200 bps speed, the Minitel standard
            bytesize = 7,    # 7-bit character size
            parity   = 'E',  # even parity
            stopbits = 1,    # 1 stop bit
            timeout  = 1,    # 1 timeout bit
            xonxoff  = False,    # no software control
            rtscts   = False     # no hardware control
        )

        self.video_teletel = VideoTeletel(self)
        self.video_telematic = VideoTelematic(self)
        self.video = self.video_teletel

        # Initializes a flag to stop the threads
        # (threads share the same variables as the main code)
        self._continue = True

        # Creates the two read/write threads
        self._threads = []
        self._threads.append(Thread(None, self._manage_input, None, ()))

        if not MODE_DIRECT:
            self._threads.append(Thread(None, self._manage_output, None, ()))

        # Starts the two read/write threads
        for thread in self._threads:
            # Configure each thread in daemon mode
            thread.setDaemon(True)
            try:
                # Starts the thread
                thread.start()
            except (KeyboardInterrupt, SystemExit):
                self.close()


    def is_terminal_connected(self) -> bool:
        """Check if the terminal is currently connected"""
        with self.connection_lock:
            return self.is_connected


    def get_input_key(self) -> Sequence|None:
        # Don't try to receive if not connected
        with self.connection_lock:
            if not self.is_connected:
                return None
        
        try:
            sequence = self.receive_sequence(blocking=False)
            myLogger.log(f"Terminal: Input Key: {sequence}")
            return sequence
        except:
            return None


    # Claude 4.5 generated
    def _optimize_clear_sequences(self, changed_cells):
        """Optimize changed cells by detecting sequences that can use clear() operations.
        
        This method analyzes changed cells to find consecutive sequences on the same row
        where cells are being cleared (set to INIT_CHAR or space with default attributes).
        If 3 or more consecutive cells are being cleared, it replaces them with a clear operation.
        
        Args:
            changed_cells: List of Cell objects that have changed
            
        Returns:
            List of Cell objects and clear operation dicts
        """
        if not changed_cells:
            return []
        
        # Sort cells by row, then column
        sorted_cells = sorted(changed_cells, key=lambda c: (c.y, c.x))
        
        optimized = []
        i = 0
        
        while i < len(sorted_cells):
            cell = sorted_cells[i]
            
            # Check if this cell is a "clear" cell (INIT_CHAR or space with default attrs)
            is_clear_cell = (
                (cell.b_char.char == INIT_CHAR or cell.b_char.char == ' ') and
                cell.b_char.attr.char_color == MINITEL_COLOR.WHITE and
                cell.b_char.attr.background_color == MINITEL_COLOR.BLACK and
                not cell.b_char.attr.underline and
                not cell.b_char.attr.blinking and
                not cell.b_char.attr.inverted
            )
            
            if is_clear_cell:
                # Look ahead to find consecutive clear cells on the same row
                clear_sequence = [cell]
                j = i + 1
                
                while j < len(sorted_cells):
                    next_cell = sorted_cells[j]
                    
                    # Check if next cell is on same row and consecutive column
                    if (next_cell.y == cell.y and 
                        next_cell.x == clear_sequence[-1].x + 1):
                        
                        # Check if it's also a clear cell
                        is_next_clear = (
                            (next_cell.b_char.char == INIT_CHAR or next_cell.b_char.char == ' ') and
                            next_cell.b_char.attr.char_color == MINITEL_COLOR.WHITE and
                            next_cell.b_char.attr.background_color == MINITEL_COLOR.BLACK and
                            not next_cell.b_char.attr.underline and
                            not next_cell.b_char.attr.blinking and
                            not next_cell.b_char.attr.inverted
                        )
                        
                        if is_next_clear:
                            clear_sequence.append(next_cell)
                            j += 1
                        else:
                            break
                    else:
                        break
                
                # If we have 3 or more consecutive clear cells, use clear operation
                if len(clear_sequence) >= 3:
                    # Use 'endline' clear - position at start and clear to end of line
                    optimized.append({
                        'type': 'clear',
                        'scope': 'endline',
                        'x': clear_sequence[0].x,
                        'y': clear_sequence[0].y,
                        'cells': clear_sequence,
                        'count': len(clear_sequence),
                        'saved': len(clear_sequence) - 1  # chars saved by using clear
                    })
                    i = j  # Skip all cells in the sequence
                else:
                    # Not enough cells to optimize, add them individually
                    for c in clear_sequence:
                        optimized.append(c)
                    i = j
            else:
                # Not a clear cell, add it normally
                optimized.append(cell)
                i += 1
        
        return optimized


    def draw_buffer(self):
        # Don't try to draw if not connected
        with self.connection_lock:
            if not self.is_connected:
                return
        
        # find all changes. copy them
        self.framebuffer.screen_lock.acquire()
        changed_cells = []
        for y, row in enumerate(self.framebuffer.screen):
            for x, cell in enumerate(row):
                if cell.a_char.char != cell.b_char.char or cell.a_char.attr != cell.b_char.attr:
                    changed_cells.append(cell.copy())
        self.framebuffer.screen_lock.release()

        # Optimize: detect sequences that can use clear() instead of individual char writes
        optimized_cells = self._optimize_clear_sequences(changed_cells)

        current_row = -1
        current_col = -1
        last_color = MINITEL_COLOR.WHITE
        last_background_color = MINITEL_COLOR.BLACK
        n = 0
        is_blinking = False
        is_underline = False
        is_inverted = False

        for item in optimized_cells:
            if isinstance(item, dict) and item.get('type') == 'clear':
                # Handle clear operation
                y = item['y']
                x = item['x']
                scope = item['scope']
                
                # Position cursor at the start of the clear
                self.video.position(x+1, y)
                current_row = y
                current_col = -1  # Reset column tracking after clear
                
                # Perform the clear operation
                self.video.clear(scope)
                
                if DEBUG:
                    myLogger.log(f"Clear operation: scope={scope} at ({x},{y}), saved {item['saved']} chars")
                
                n += item['count']
                continue
            
            # Handle normal cell drawing (item is a Cell)
            cell = cast(Cell, item)
            if DEBUG:
                myLogger.log(f"Changed Cell at ({cell.x},{cell.y}): a_char='{cell.a_char.char}' (0x{cell.a_char.char.encode().hex()}) b_char='{cell.b_char.char}' (0x{cell.b_char.char.encode().hex()})")
            y  = cell.y
            x  = cell.x

            # Position Cursor - first if needed (for color to work properly)
            if current_row != y or current_col != x:
                # x is 1-based
                # y line 0 is status bar, but valid
                self.video.position(x+1, y)
                current_row = y
                current_col = x

            # color, fg bg
            if cell.b_char.attr.char_color != last_color:
                last_color = cell.b_char.attr.char_color
                #self.send([ESC, 0x40 + cell.b_char.attr.char_color.value])
                self.video.color(cell.b_char.attr.char_color.value, None)
            if cell.b_char.attr.background_color != last_background_color:
                last_background_color = cell.b_char.attr.background_color
                #self.send([ESC, 0x50 + cell.b_char.attr.background_color.value])
                self.video.color(None, cell.b_char.attr.background_color.value)

            # underline
            if cell.b_char.attr.underline != is_underline:
                if cell.b_char.attr.underline:
                    self.video.effect(True, None, None)
                    is_underline = True
                else:
                    self.video.effect(False, None, None)
                    is_underline = False

            # blinking
            if cell.b_char.attr.blinking != is_blinking:
                if cell.b_char.attr.blinking:
                    self.video.effect(None, True, None)
                    is_blinking = True
                else:
                    self.video.effect(None, False, None)
                    is_blinking = False

            # inverted
            if cell.b_char.attr.inverted != is_inverted:
                if cell.b_char.attr.inverted:
                    self.video.effect(None, None, True)
                    is_inverted = True
                else:
                    self.video.effect(None, None, False)
                    is_inverted = False

            # send to minitel
            # If the new char is INIT_CHAR, it is basically deleted
            # Change it to a whitespace instead for display purposes
            if cell.b_char.char == INIT_CHAR:
                self.send(' ')
            else:
                self.send(cell.b_char.char)
            current_col += 1  # Update our tracking of current column
            n += 1

        # NOTE: update the screen, indicate what we have written
        self.framebuffer.screen_lock.acquire()
        for item in optimized_cells:
            if isinstance(item, dict) and item.get('type') == 'clear':
                # Update all cells affected by the clear operation
                for cell in item['cells']:
                    y = cell.y
                    x = cell.x
                    self.framebuffer.screen[y][x].a_char.char = cell.b_char.char
                    self.framebuffer.screen[y][x].a_char.attr.char_color = cell.b_char.attr.char_color
                    self.framebuffer.screen[y][x].a_char.attr.background_color = cell.b_char.attr.background_color
                    self.framebuffer.screen[y][x].a_char.attr.underline = cell.b_char.attr.underline
                    self.framebuffer.screen[y][x].a_char.attr.blinking = cell.b_char.attr.blinking
                    self.framebuffer.screen[y][x].a_char.attr.inverted = cell.b_char.attr.inverted
                continue
            
            # Update single cell
            cell = cast(Cell, item)
            y = cell.y
            x = cell.x
            self.framebuffer.screen[y][x].a_char.char = cell.b_char.char
            self.framebuffer.screen[y][x].a_char.attr.char_color = cell.b_char.attr.char_color
            self.framebuffer.screen[y][x].a_char.attr.background_color = cell.b_char.attr.background_color
            self.framebuffer.screen[y][x].a_char.attr.underline = cell.b_char.attr.underline
            self.framebuffer.screen[y][x].a_char.attr.blinking = cell.b_char.attr.blinking
            self.framebuffer.screen[y][x].a_char.attr.inverted = cell.b_char.attr.inverted
        self.framebuffer.screen_lock.release()

        if DEBUG and n > 0:
            myLogger.log(f"Redrew {n} chars")


    def close(self):
        """Closes the connection with the Minitel

        Tells the send/receive threads that they should stop and
        waits for them to stop. Since the send and receive timeouts are
        set to 1 second, this is the average time this method will take
        to execute.
        """
        # Tells the threads that they should stop all activity
        self._continue = False

        # Waits for all threads to finish
        for thread in self._threads:
            thread.join()

        self._minitel.close()

    def _manage_input(self):
        """Manages character sequences sent from the Minitel

        This method should not be called directly, it is reserved
        exclusively for the Minitel class. It loops indefinitely trying
        to read a character on the serial connection.
        """
        # Adds to the input_queue queue everything the Minitel can send
        while self._continue:
            # Waits for a character for 1 second
            character = self._minitel.read()

            if len(character) == 1:
                byte_value = character[0]
                
                # Check for 0x00 byte which indicates terminal power on/off
                if byte_value == 0x00:
                    with self.connection_lock:
                        if not self.is_connected:
                            # Terminal turned ON
                            myLogger.log("Terminal: Minitel connected (power on detected)")
                            self.is_connected = True
                            # Re-initialize the terminal
                            try:
                                self.terminal_init_videotex()
                                myLogger.log("Terminal: Re-initialized videotex mode")
                            except Exception as e:
                                myLogger.log(f"Terminal: Error during re-initialization: {e}")
                            # clear buffer so redraw is forced
                            self.framebuffer.reset_buffer()
                        else:
                            # Terminal turned OFF
                            myLogger.log("Terminal: Minitel disconnected (power off detected)")
                            self.is_connected = False
                    # Don't put 0x00 bytes in the input queue
                    continue
                
                # Only queue normal characters if connected
                with self.connection_lock:
                    if self.is_connected:
                        self.input_queue.put(character)

    def _manage_output(self):
        """Manages character sequences sent to the Minitel

        This method should not be called directly, it is reserved
        exclusively for the Minitel class. It loops indefinitely trying
        to read a character from the output queue.
        """
        # Sends to the Minitel everything in the output queue and
        # continues to do so as long as the continue flag is true
        while self._continue or not self.output_queue.empty():
            # Waits for a character for 1 second
            try:
                output_unicode = self.output_queue.get(block = True, timeout = 1)
                self._minitel.write(output_unicode.encode())

                # Waits for the character sent to the minitel to have been sent
                # because the output is buffered
                self._minitel.flush()

                # Allows the queue's join method to work
                self.output_queue.task_done()

            except Empty:
                continue

    def send(self, content):
        """Sends a character sequence

        Sends a character sequence to the Minitel.

        :param content:
            A character sequence interpretable by the Sequence class.
        :type content:
            a Sequence object, a string or unicode, a list,
            an integer
        """

        # Converts any input to a Sequence object
        if not isinstance(content, Sequence):
            content = Sequence(content)

        if MODE_DIRECT:
            # write the characters one by one directly to the minitel
            # bypassing the output queue
            for value in content.valeurs:
                self._minitel.write(chr(value).encode())
            self._minitel.flush()
        else:
            # Adds the characters one by one to the send queue
            for value in content.valeurs:
                self.output_queue.put(chr(value))

    def receive(self, blocking = False, wait = None):
        """Reads a character from the Minitel

        Returns a character present in the receive queue.

        :param blocking:
            True to wait for a character if there is none in the
            receive queue. False to not wait and
            return immediately.
        :type blocking:
            a boolean

        :param wait:
            wait in seconds, values below one second
            accepted. Valid only in block = True mode
            If wait = None and block = True, then we wait
            indefinitely for a character to arrive.
        :type wait:
            an integer, or None

        :raise Empty:
            Raises an Empty exception if block = True
            and the waiting time has been exceeded
        """
        assert blocking in [True, False]
        assert isinstance(wait, (int,float)) or wait == None

        return self.input_queue.get(blocking, wait).decode()

    def receive_sequence(self,blocking = True, wait=None):
        """Reads a sequence from the Minitel

        Returns a Sequence object received from the Minitel. This function
        analyzes the Minitel's transmissions to make a consistent sequence
        from the Minitel's point of view. For example, if the Minitel sends a
        SS2, SEP or ESC character, it only announces a sequence of
        characters designating a result or a character that does not exist in the
        ASCII standard. On the other hand, the number of characters that can be received
        after special characters is standardized. This allows to know
        exactly the number of characters that will constitute the sequence.

        It is this method that should be used rather than the
        receive method when communicating with the Minitel.

        :param blocking:
            True to wait for a sequence if there is none in the
            receive queue. False to not wait and
            return immediately.
        :type blocking:
            a boolean

        :param wait:
            wait in seconds, values below one second
            accepted. Valid only in block = True mode
            If wait = None and block = True, then we wait
            indefinitely for a character to arrive.
        :type wait:
            an integer, or None

        :returns:
            a Sequence object
        """
        # Creates a sequence
        sequence = Sequence()

        # Adds the first character read to the sequence in blocking mode
        sequence.ajoute(self.receive(blocking = blocking, wait = wait))
        assert sequence.longueur != 0

        # Tests the received character
        if sequence.valeurs[-1] in [SS2, SEP]:
            # A sequence starting with SS2 or SEP will have a length of 2
            sequence.ajoute(self.receive(blocking = True))
        elif sequence.valeurs[-1] == ESC:
            # ESC sequences have variable sizes ranging from 1 to 4
            try:
                # Tries to read a character with a wait time of 1/10s
                # This allows to read the Esc key which sends
                # only the ESC code without anything after.
                sequence.ajoute(self.receive(blocking = True, wait = 0.1))

                # A CSI sequence starts with ESC, 0x5b
                if sequence.valeurs == CSI:
                    # A CSI sequence calls for at least 1 character
                    sequence.ajoute(self.receive(blocking = True))

                    if sequence.valeurs[-1] in [0x32, 0x34]:
                        # The sequence ESC, 0x5b, 0x32/0x34 calls for a last
                        # character
                        sequence.ajoute(self.receive(blocking = True))
            except Empty:
                # If no character has occurred after 1/10s, we continue
                pass

        if DEBUG:
            myLogger.log(f"Terminal: Received sequence: {sequence}")
        return sequence

    def call(self, content, wait):
        """Sends a sequence to the Minitel and waits for its response.

        This method allows to send a command to the Minitel (configuration,
        status query) and to wait for its response. This function waits
        at most 1 second before giving up. In this case, an empty
        sequence is returned.

        Before launching the command, the method empties the receive
        queue.

        :param content:
            A character sequence interpretable by the
            Sequence class
        :type content:
            a Sequence object, a string, a unicode string
            or an integer

        :param wait:
            Number of characters expected from the Minitel in
            response to our sending.
        :type wait:
            an integer

        :returns:
            a Sequence object containing the Minitel's response to the
            command sent.
        """
        assert isinstance(wait, int)

        # Empties the receive queue
        self.input_queue = Queue()

        # Sends the sequence
        self.send(content)

        # Waits for the entire sequence to have been sent
        self.output_queue.join()

        # Tries to receive the number of characters indicated by the
        # wait parameter with a delay of 1 second.
        response = Sequence()
        for _ in range(0, wait):
            try:
                # Waits for a character
                input_bytes = self.input_queue.get(block = True, timeout = 1)
                response.ajoute(input_bytes.decode())
            except Empty:
                # If a character has not been sent in less than a second,
                # we give up
                break

        return response
    

    def terminal_init_videotex(self):
        self.video = self.video_teletel
        self.configure_keyboard(extended=True, cursor=False, lowercase=True)
        self.video.echo(False)
        self.video.clear()
        self.video.cursor(False)
        self.cursor_x = 0
        self.cursor_y = 1


    def set_new_video_mode(self, mode: MinitelVideoMode) -> bool:
        # If the requested mode is already active, do nothing
        if self.mode == mode:
            return True

        myLogger.log(f"Terminal: Change gfx mode from {self.mode} to {mode}")
        if mode == MinitelVideoMode.VIDEOTEX:
            if not self._set_mode(MinitelVideoMode.VIDEOTEX):
                myLogger.log("Error changing videomode 0")
            self.terminal_init_videotex()
        elif mode == MinitelVideoMode.TELEMATIC:
            if not self._set_mode(MinitelVideoMode.TELEMATIC):
                myLogger.log("Error changing videomode 1")
            self.video = self.video_telematic

            #self.video.echo(False)
            #self.video.cursor(False)
        return True


    def _set_mode(self, mode = MinitelVideoMode.VIDEOTEX) -> bool:
        """Defines the Minitel's operating mode.

        The Minitel can operate in 3 modes: VideoTex (the standard
        Minitel mode, the one when switched on), Mixed or Tele-Informatique (an
        80-column mode).

        The definir_mode method takes into account the current mode of the Minitel to
        issue the correct command.

        :param mode:
            a value among the following: VIDEOTEX,
            MIXTE or TELEINFORMATIQUE (case is important).
        :type mode:
            a string

        :returns:
            False if the mode change could not take place, True otherwise.
        """
        result: bool = False

        # There are 9 possible cases, but only 6 are relevant. The cases
        # requesting to switch from VIDEOTEX to VIDEOTEX, for example, do not give
        # rise to any transaction with the Minitel
        if self.mode == MinitelVideoMode.TELEMATIC and mode == MinitelVideoMode.VIDEOTEX:
            response = self.call([CSI, 0x3f, 0x7b], 2)
            result = response.egale([SEP, 0x5e])
        elif self.mode == MinitelVideoMode.TELEMATIC and mode == MinitelVideoMode.MIXED:
            # There is no command to switch directly from
            # Tele-Informatique mode to Mixed mode. We therefore perform the
            # transition in two steps by going through Videotex mode
            response = self.call([CSI, 0x3f, 0x7b], 2)
            result = response.egale([SEP, 0x5e])

            if not result:
                return False

            response = self.call([PRO2, MIXED1], 2)
            result = response.egale([SEP, 0x70])
        elif self.mode == MinitelVideoMode.VIDEOTEX and mode == MinitelVideoMode.MIXED:
            response = self.call([PRO2, MIXED1], 2)
            result = response.egale([SEP, 0x70])
        elif self.mode == MinitelVideoMode.VIDEOTEX and mode == MinitelVideoMode.TELEMATIC:
            response = self.call([PRO2, TELINFO], 4)
            result = response.egale([CSI, 0x3f, 0x7a])
        elif self.mode == MinitelVideoMode.MIXED and mode == MinitelVideoMode.VIDEOTEX:
            response = self.call([PRO2, MIXED2], 2)
            result = response.egale([SEP, 0x71])
        elif self.mode == MinitelVideoMode.MIXED and mode == MinitelVideoMode.TELEMATIC:
            response = self.call([PRO2, TELINFO], 4)
            result = response.egale([CSI, 0x3f, 0x7a])

        # If the change has taken place, we keep the new mode in memory
        if result:
            self.mode = mode

        return result

    def identify_capabilities(self):
        """Identifies the connected Minitel.

        This method must be called once the connection with the
        Minitel has been established in order to determine the available
        functionalities and characteristics.

        No value is returned. Instead, the capabilities attribute of
        the object contains a dictionary of values providing information on the
        Minitel's capabilities:

        - capabilities['name'] -- Name of the Minitel (e.g. Minitel 2)
        - capabilities['returnable'] -- Can the Minitel be returned and
          serve as a modem? (True or False)
        - capabilities['keyboard'] -- Keyboard (None, ABCD or Azerty)
        - capabilities['speed'] -- Max speed in bps (1200, 4800 or 9600)
        - capabilities['manufacturer'] -- Manufacturer's name (e.g. Philips)
        - capabilities['80columns'] -- Can the Minitel display 80
          columns? (True or False)
        - capabilities['characters'] -- Can characters be redefined?
          (True or False)
        - capabilities['version'] -- Software version (a letter)
        """
        self.capabilities = BASIC_CAPABILITIES

        # Issues the identification command
        response = self.call([PRO1, ENQROM], 5)

        # Tests the validity of the response
        if (response.longueur != 5 or
            response.valeurs[0] != SOH or
            response.valeurs[4] != EOT):
            myLogger.log("Terminal: Identify Capabilities: Response error (is Terminal set to telematic instead of teletel?)")
            return

        # Extracts the identification characters
        minitel_manufacturer = chr(response.valeurs[1])
        minitel_type         = chr(response.valeurs[2])
        software_version     = chr(response.valeurs[3])

        # Minitel types
        if minitel_type in TYPE_MINITELS:
            self.capabilities = TYPE_MINITELS[minitel_type]

        if minitel_manufacturer in MANUFACTURERS:
            self.capabilities['constructeur'] = MANUFACTURERS[minitel_manufacturer]

        self.capabilities['version'] = software_version

        # Manufacturer correction
        if minitel_manufacturer == 'B' and minitel_type == 'v':
            self.capabilities['constructeur'] = 'Philips'
        elif minitel_manufacturer == 'C':
            if software_version == ['4', '5', ';', '<']:
                self.capabilities['constructeur'] = 'Telic ou Matra'

        # Manufacturer correction
        if minitel_manufacturer == 'B' and minitel_type == 'v':
            self.capabilities['constructeur'] = 'Philips'
        elif minitel_manufacturer == 'C':
            if software_version == ['4', '5', ';', '<']:
                self.capabilities['constructeur'] = 'Telic ou Matra'
        myLogger.log(f"Terminal Capabilities: {self.capabilities['constructeur']} {self.capabilities['name']} {self.capabilities['speed']} 80:{self.capabilities['80columns']} Redef:{self.capabilities['characters']} V:{self.capabilities['version']}")


    def identify_mode(self):
        # Determines the screen mode in which the Minitel is
        response = self.call([PRO1, OPERATING_STATUS], PRO2_LENGTH)
        if response.longueur != PRO2_LENGTH:
            # The Minitel is in Tele-informatique mode because it does not respond
            # to a protocol command
            self.mode = MinitelVideoMode.TELEMATIC
        elif response.valeurs[3] & 1 == 1:
            # Bit 1 of the operating status indicates 80-column mode
            self.mode = MinitelVideoMode.MIXED
        else:
            # By default, we consider that we are in Videotex mode
            self.mode = MinitelVideoMode.VIDEOTEX

        myLogger.log(f"Terminal: VideoMode: {self.mode}")


    # Note: This doesnt seem to work for minitel 1 to identify 4800
    def guess_speed(self):
        """Guess the connection speed with the Minitel.
F
        This method should be called right after creating the object
        in order to automatically determine the transmission speed on
        which the Minitel is set.

        To perform the detection, the guess_speed method will test the
        speeds 9600 bps, 4800 bps, 1200 bps and 300 bps (in this order) and
        send a PRO1 terminal status request command each time.
        If the Minitel responds with a PRO2 acknowledgement, we have detected the speed.

        In case of detection, the speed is recorded in the speed attribute
        of the object.

        :returns:
            The method returns the speed in bits per second or -1 if it
            could not be determined.
        """
        # Possible speeds up to Minitel 2
        speeds = [9600, 4800, 1200, 300]

        for speed in speeds:
            # Configures the serial port to the speed to be tested
            self._minitel.baudrate = speed

            # Sends a terminal status request
            response = self.call([PRO1, TERMINAL_STATUS], PRO2_LENGTH)

            # The Minitel must return a PRO2 acknowledgement
            if response.longueur == PRO2_LENGTH:
                myLogger.log(f"Terminal GuessSpeed: {speed}")
                self.speed = speed
                return speed

        # The speed was not found
        return -1

    def set_speed(self, speed):
        """Programs the Minitel and the serial port for a given speed.

        To change the communication speed between the computer and the
        Minitel, the developer must first ensure that the connection with
        the Minitel has been established at the correct speed (see the
        guess_speed method).

        This method should only be called after the Minitel has been
        identified (see the identifier method) because it is based on the
        detected capabilities of the Minitel.

        The method first sends a speed setting command to the Minitel
        and, if it accepts it, configures the serial port to the new
        speed.

        :param speed:
            speed in bits per second. Accepted values are 300, 1200,
            4800 and 9600. The value 9600 is only allowed from Minitel
            2
        :type speed:
            an integer

        :returns:
            True if the speed could be programmed, False otherwise.
        """
        assert isinstance(speed, int)

        # Possible speeds up to Minitel 2
        speeds = {300: B300, 1200: B1200, 4800: B4800, 9600: B9600}

        # Tests the validity of the requested speed
        if speed not in speeds or speed > self.capabilities['speed']:
            return False

        # Sends a protocol command for speed programming
        response = self.call([PRO2, PROG, speeds[speed]], PRO2_LENGTH)

        # The Minitel must return a PRO2 acknowledgement
        if response.longueur == PRO2_LENGTH:
            # If we can read a PRO2 acknowledgement before having set the
            # serial port speed, it means that the Minitel cannot use
            # the requested speed
            return False

        # Configures the serial port to the new speed
        self._minitel.baudrate = speed
        self.speed = speed

        return True

    def configure_keyboard(self, extended = False, cursor = False,
                           lowercase = False):
        """Configures the keyboard operation.

        Configures the operation of the Minitel keyboard. This impacts the
        codes and characters that the Minitel can send to the computer
        depending on the keys pressed (alphabetic keys, function
        keys, key combinations, etc.).

        The method returns True if all configuration commands have
        been correctly processed by the Minitel. As soon as a command fails,
        the method stops immediately and returns False.

        :param extended:
            True for an extended mode keyboard, False for a normal
            mode keyboard
        :type extended:
            a boolean

        :param cursor:
            True if the cursor keys should be managed, False otherwise
        :type cursor:
            a boolean

        :param lowercase:
            True if pressing an alphabetic key without simultaneously
            pressing the Shift key should generate a lowercase letter, False if
            it should generate an uppercase letter.
        :type lowercase:
            a boolean
        """
        assert extended in [True, False]
        assert cursor in [True, False]
        assert lowercase in [True, False]

        # The keyboard commands work on a start/stop
        # toggle principle
        toggles = { True: START, False: STOP }

        # Creates the sequences of the 3 calls according to the arguments
        calls = [
            ([PRO3, toggles[extended   ], RECV_KEYBOARD, EXTENDED], PRO3_LENGTH),
            ([PRO3, toggles[cursor  ], RECV_KEYBOARD, C0  ], PRO3_LENGTH),
            ([PRO2, toggles[lowercase], LOWERCASE        ], PRO2_LENGTH)
        ]

        # Sends the commands one by one
        for call in calls:
            command = call[0] # First element of the tuple = command
            length = call[1] # Second element of the tuple = response length

            response = self.call(command, length)

            if response.longueur != length:
                return False

        return True

    
    def semigraphic(self, active = True):
        """Switches to semi-graphic mode or alphabetic mode

        :param active:
            True to switch to semi-graphic mode, False to return to
            normal mode
        :type active:
            a boolean
        """
        assert active in [True, False]

        actives = { True: SO, False: SI}
        self.send(actives[active])


    def redefine(self, from_char, drawings, charset = 'G0'):
        """Redefines Minitel characters

        From Minitel 2, it is possible to redefine characters.
        Each character is drawn from an 8×10 pixel matrix.

        The character designs are given by a sequence of 0s and 1s in
        a string. Any other character is purely and
        simply ignored. This particularity allows to draw the
        characters from a standard text editor and to add
        comments.
        
        Example::

            11111111
            10000001
            10000001
            10000001
            10000001 This is a rectangle!
            10000001
            10000001
            10000001
            10000001
            11111111

        The Minitel does not insert any separation pixels between the characters,
        so you have to take this into account and include them in your drawings.

        Once the character(s) have been redefined, the special character set
        containing them is automatically selected and they can therefore
        be used immediately.

        :param from_char:
            character from which to redefine
        :type from_char:
            a string
        :param drawings:
            drawings of the characters to be redefined
        :type drawings:
            a string
        :param charset:
            character palette to modify (G0 or G1)
        :type charset:
            a string
        """
        assert charset == 'G0' or charset == 'G1'
        assert isinstance(from_char, str) and len(from_char) == 1
        assert isinstance(drawings, str)

        # Two sets are available G’0 and G’1
        if charset == 'G0':
            self.send([US, 0x23, 0x20, 0x20, 0x20, 0x42, 0x49])
        else:
            self.send([US, 0x23, 0x20, 0x20, 0x20, 0x43, 0x49])

        # We indicate from which character we want to redefine the drawings
        self.send([US, 0x23, from_char, 0x30])

        byte_str = ''
        pixel_count = 0
        for pixel in drawings:
            # Only the characters 0 and 1 are interpreted, the others are
            # ignored. This allows to present the drawings in the source
            # code in a more readable way
            if pixel != '0' and pixel != '1':
                continue

            byte_str = byte_str + pixel
            pixel_count += 1

            # We group the pixels of the character in packets of 6
            # because we can only send 6 bits at a time
            if len(byte_str) == 6:
                self.send(0x40 + int(byte_str, 2))
                byte_str = ''

            # When 80 pixels (8 columns × 10 lines) have been sent
            # we add 4 bits to zero because the sending is done in packets of 6 bits
            # (8×10 = 80 pixels, 14×6 = 84 bits, 84-80 = 4)
            if pixel_count == 80:
                self.send(0x40 + int(byte_str + '0000', 2))
                self.send(0x30)
                byte_str = ''
                pixel_count = 0

        # Positioning the cursor allows to exit the definition mode
        self.send([US, 0x41, 0x41])

        # Selects the freshly modified character set (G’0 or G’1)
        if charset == 'GO':
            self.send([ESC, 0x28, 0x20, 0x42])
        else:
            self.send([ESC, 0x29, 0x20, 0x43])

