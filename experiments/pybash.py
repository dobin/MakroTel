#!/usr/bin/env python3
"""
Spawn a bash shell attached to a pseudo-TTY (80x25 by default) and bridge it
to a serial port using pyserial.

This script runs on POSIX systems (Linux/macOS). It creates a pty pair,
spawns /bin/bash with the slave side as its controlling tty, applies a
specified window size (rows x cols), and then proxies bytes between the
pty master and a serial port using selectors.

Usage:
    sudo python3 bash_serial_terminal.py --port /dev/ttyUSB0 --baud 115200

Note: Accessing serial devices typically requires appropriate permissions
or running as root.
"""

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

try:
    import serial
except Exception as e:
    print("pyserial not installed. Install with: pip install pyserial")
    raise


TIOCSWINSZ = getattr(termios, 'TIOCSWINSZ', None)


def set_pty_winsize(fd, rows, cols):
    """Set the terminal window size for the slave side of the pty.

    fd: file descriptor (should be the slave side)
    rows, cols: integers
    """
    if TIOCSWINSZ is None:
        return
    # struct winsize: unsigned short rows, cols, xpixels, ypixels
    winsize = struct.pack('HHHH', rows, cols, 0, 0)
    fcntl.ioctl(fd, TIOCSWINSZ, winsize)


def open_serial(port, baud, timeout=0):
    """Open and return a pyserial Serial object in non-blocking mode."""
    ser = serial.Serial(
        port,
        baudrate = 1200, # 1200 bps speed, the Minitel standard
        bytesize = 7,    # 7-bit character size
        parity   = 'E',  # even parity
        stopbits = 1,    # 1 stop bit
        timeout  = 1,    # 1 timeout bit
        xonxoff  = False,    # no software control
        rtscts   = False     # no hardware control
    )
    return ser


def spawn_bash(slave_fd, env=None):
    """Spawn bash with the slave fd as stdin/stdout/stderr."""   
    # Make sure slave_fd is a proper file descriptor
    # We duplicate fd into 0/1/2 in the child
    # Use preexec_fn to set the session id so the pty becomes the controlling tty
    def _preexec():
        os.setsid()
        # Make the slave the controlling terminal
        try:
            # TIOCSCTTY is Linux-specific; ignore failures
            import termios as _t
            TIOCSCTTY = getattr(_t, 'TIOCSCTTY', None)
            if TIOCSCTTY is not None:
                fcntl.ioctl(slave_fd, TIOCSCTTY, 0)
        except Exception:
            pass

    env = os.environ.copy()
    env["TERM"] = "minitel"   # or "vt100", or "minitel" if you install a terminfo entry

    # Duplicate slave fd into child's std fds using pass_fds or direct duplication
    # We'll use os.dup to make separate fds for the child
    child = subprocess.Popen(
        ['/bin/bash'],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        preexec_fn=_preexec,
        close_fds=False,
        env=env,
    )
    return child


def bridge(master_fd, ser):
    """Bridge data between pty master fd and serial.Serial instance."""
    sel = selectors.DefaultSelector()
    sel.register(master_fd, selectors.EVENT_READ, data='pty')
    sel.register(ser.fileno(), selectors.EVENT_READ, data='serial')

    try:
        while True:
            events = sel.select(timeout=1.0)
            if not events:
                # optionally perform periodic checks
                continue
            for key, mask in events:
                if key.data == 'pty':
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError as e:
                        if e.errno == errno.EIO:
                            # slave closed
                            return
                        raise
                    if not data:
                        # EOF
                        return
                    # write to serial
                    ser.write(data)
                elif key.data == 'serial':
                    data = ser.read(4096)
                    if data:
                        os.write(master_fd, data)
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(description='Spawn bash on a pty and bridge to serial port')
    parser.add_argument('--port', default="/dev/ttyUSB0", help='Serial device (e.g. /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=1200, help='Serial baud rate')
    parser.add_argument('--rows', type=int, default=25, help='Terminal rows')
    parser.add_argument('--cols', type=int, default=80, help='Terminal cols')
    parser.add_argument('--shell', default='/bin/bash', help='Shell to run')
    args = parser.parse_args()

    if os.name != 'posix':
        print('This script requires POSIX (Linux/macOS).')
        sys.exit(1)

    # Open serial port
    print(f"Opening serial port {args.port} @ {args.baud}")
    ser = open_serial(args.port, args.baud)

    # Create pty
    master_fd, slave_fd = os.openpty()
    slave_name = os.ttyname(slave_fd)
    print(f"Created pty slave: {slave_name}")

    # Set terminal window size on slave
    set_pty_winsize(slave_fd, args.rows, args.cols)

    # Spawn the shell using the slave fd
    # Duplicate the slave fd so subprocess can safely use it
    slave_for_child = os.dup(slave_fd)

    # Close the slave in the parent after dup
    os.close(slave_fd)

    # Spawn shell
    child = subprocess.Popen(
        [args.shell],
        stdin=slave_for_child,
        stdout=slave_for_child,
        stderr=slave_for_child,
        preexec_fn=os.setsid,
        close_fds=False,
    )

    # parent no longer needs the duplicate fd
    os.close(slave_for_child)

    print(f"Spawned shell pid={child.pid}")

    try:
        bridge(master_fd, ser)
    finally:
        try:
            ser.close()
        except Exception:
            pass
        try:
            os.close(master_fd)
        except Exception:
            pass
        # Try to terminate child
        try:
            child.terminate()
        except Exception:
            pass


if __name__ == '__main__':
    main()
