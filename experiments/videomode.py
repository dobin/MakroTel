#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import selectors
import fcntl
import struct
import termios
import errno
import time
import serial


ser = serial.Serial(
    "/dev/ttyUSB0",
    baudrate = 1200, # 1200 bps speed, the Minitel standard
    bytesize = 7,    # 7-bit character size
    parity   = 'E',  # even parity
    stopbits = 1,    # 1 stop bit
    timeout  = 1,    # 1 timeout bit
    xonxoff  = False,    # no software control
    rtscts   = False     # no hardware control
)

#ser.write(b"\x1b\x64")

# to telematic
ser.write(b"\x1b\x3a\x31\x7d")
ser.write(b"--------------------------------------------")

time.sleep(1)

# to minitel
ser.write(b"\x1b\x5b\x3f\x7b")
ser.write(b"--------------------------------------------")
