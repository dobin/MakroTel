#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Minitel universal constants definitions"""


# ASCII control codes
NUL = 0x00 # null
SOH = 0x01 # start of heading
STX = 0x02 # start of text
ETX = 0x03 # end of text
EOT = 0x04 # end of transmission
ENQ = 0x05 # enquiry
ACK = 0x06 # acknowledge
BEL = 0x07 # bell
BS  = 0x08 # backspace
TAB = 0x09 # horizontal tab
LF  = 0x0a # line feed, new line
VT  = 0x0b # vertical tab
FF  = 0x0c # form feed, new page
CR  = 0x0d # carriage return
SO  = 0x0e # shift out
SI  = 0x0f # shift in
DLE = 0x10 # data link escape
DC1 = 0x11 # device control 1
CON = 0x11 # Cursor on
DC2 = 0x12 # device control 2
REP = 0x12 # Rep
DC3 = 0x13 # device control 3
SEP = 0x13 # Sep
DC4 = 0x14 # device control 4
COF = 0x14 # Cursor off
NAK = 0x15 # negative acknowledge
SYN = 0x16 # synchronous idle
ETB = 0x17 # end of transmission block
CAN = 0x18 # cancel
EM  = 0x19 # end of medium
SS2 = 0x19 # SS2
SUB = 0x1a # substitute
ESC = 0x1b # escape
FS  = 0x1c # file separator
GS  = 0x1d # group separator
SS3 = 0x1d # SS3
RS  = 0x1e # record separator
US  = 0x1f # unit separator

PRO1 = [ESC, 0x39] # protocol 1
PRO2 = [ESC, 0x3a] # protocol 2
PRO3 = [ESC, 0x3b] # protocol 3
CSI  = [ESC, 0x5b] # CSI

# PRO1 commands
DISCONNECT = 0x67
CONNECT = 0x68
RET1 = 0x6c
RET2 = 0x6d
OPPO = 0x6f
TERMINAL_STATUS = 0x70
KEYBOARD_STATUS = 0x72
OPERATING_STATUS = 0x72
SPEED_STATUS = 0x74
PROTOCOL_STATUS = 0x76
ENQROM = 0x7b
RESET = 0x7f

# PRO2 commands
COPY = 0x7c
ROUTING_TO = 0x62
NO_BROADCAST = 0x64
NO_ACK_RETURN = 0x64
BROADCAST = 0x65
ACK_RETURN = 0x65
TRANSPARENCY = 0x66
START = 0x69
STOP = 0x6a
PROG = 0x6b
KEYBOARD_STATUS_REP = 0x73
OPERATING_STATUS_REP = 0x73
PROTOCOL_STATUS_REP = 0x77
TELINFO = [0x31, 0x7d]
MIXED1 = [0X32, 0X7d]
MIXED2 = [0X32, 0X7e]

# PRO3 commands
ROUTING_OFF = 0x60
ROUTING_ON = 0x61
ROUTING_FROM = 0x63

# PRO command lengths
PRO1_LENGTH = 3
PRO2_LENGTH = 4
PRO3_LENGTH = 5

# Other codes
FRENCH_COPY = 0x6a
AMERICAN_COPY = 0x6b
EXTENDED = 0x41
C0 = 0x43

# PRO2+START/STOP codes
SCROLL = 0x43
PROCEDURE = 0x44
LOWERCASE = 0x45

# PRO2+PROG codes
B9600 = 0x7f
B4800 = 0x76
B1200 = 0x64
B300 = 0x52

# PRO3+START/STOP codes
EXTENDED = 0x41
C0 = 0x43

# Reception codes
RECV_SCREEN = 0x58
RECV_KEYBOARD = 0x59
RECV_MODEM = 0x5a
RECV_PERIPHERAL = 0x5b

# Emission codes
SEND_SCREEN = 0x50
SEND_KEYBOARD = 0x51
SEND_MODEM = 0x52
SEND_PERIPHERAL = 0x53

# Accents
ACCENT_CEDILLA = [SS2, 0x4b]
ACCENT_GRAVE = [SS2, 0x41]
ACCENT_ACUTE = [SS2, 0x42]
ACCENT_CIRCUMFLEX = [SS2, 0x43]
ACCENT_TREMA = [SS2, 0x48]

# Direction keys
UP = [CSI, 0x41]
DOWN = [CSI, 0x42]
LEFT = [CSI, 0x44]
RIGHT = [CSI, 0x43]

SHIFT_UP = [CSI, 0x4D]
SHIFT_DOWN = [CSI, 0x4C]
SHIFT_LEFT = [CSI, 0x50]
SHIFT_RIGHT = [CSI, 0x34, 0x68]

CTRL_LEFT = 0x7f

# Enter/Carriage return key
ENTER      = 0x0d
SHIFT_ENTER  = [CSI, 0x48]
CTRL_ENTER = [CSI, 0x32, 0x4a]

# Function keys
SEND       = [DC3, 0x41]
RETURN     = [DC3, 0x42]
REPEAT     = [DC3, 0x43]
GUIDE      = [DC3, 0x44]
CANCEL     = [DC3, 0x45]
SUMMARY    = [DC3, 0x46]
CORRECTION = [DC3, 0x47]
NEXT       = [DC3, 0x48]
CONNECTION_KEY  = [DC3, 0x49]

# The gray levels are staggered as follows:
# black, blue, red, magenta, green, cyan, yellow, white
MINITEL_COLORS = {
    'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
    'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7,
    '0': 0, '1': 4, '2': 1, '3': 5,
    '4': 2, '5': 6, '6': 3, '7': 7,
    0: 0, 1: 4, 2: 1, 3: 5,
    4: 2, 5: 6, 6: 3, 7: 7
}
