# RS485 support
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

"""\
The settings for RS485 are stored in a dedicated object that can be applied to
serial ports (where supported).
NOTE: Some implementations may only support a subset of the settings.
"""

from __future__ import absolute_import

import time
import serial.rs485


if __name__=="__main__":
    ser = serial.rs485.RS485(
        port='/dev/ttyUSB0',  # Replace with the appropriate serial port
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE,
        timeout=0
    )
    print(ser.is_open)
    ser.rs485_mode = serial.rs485.RS485Settings()
    print(ser.rs485_mode)
    packet = bytearray()
    packet.append(0x02)
    packet.append(0x43)
    packet.append(0xb0)
    packet.append(0x01)
    packet.append(0x03)
    packet.append(0xf2)
    command = bytes(packet)
    print(command)
    while True:
        print(ser.write(command))
        print(ser.read())

    ser.close()

