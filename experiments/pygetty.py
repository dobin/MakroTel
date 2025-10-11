import os
import pty
import serial
import subprocess
import select

# open the physical serial port
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

# create a pty
master_fd, slave_fd = pty.openpty()
slave_name = os.ttyname(slave_fd)

# spawn agetty on the slave side
subprocess.Popen(['agetty', '-L', '1200', slave_name])

# now forward data between serial and the master side of the pty
while True:
    rlist, _, _ = select.select([ser, master_fd], [], [])
    if ser in rlist:
        data = ser.read(ser.in_waiting or 1)
        os.write(master_fd, data)
    if master_fd in rlist:
        data = os.read(master_fd, 1024)
        ser.write(data)