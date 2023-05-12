# -*- coding: utf-8 -*-
import pyb
import uos

"""
Duplicate stdout/terminal to serial port on one of the pins.

Reference port bindings:
Ser 1:    Rx X10      Tx X9
Ser 2:    Rx X4       Tx X3
Ser 3:    Rx Y10      Tx Y9
Ser 4:    Rx X2       Tx X1
Ser 6:    Rx Y2       Tx Y1
"""
DUP_PORT = 3
DUP_SPEED = 38400

termrep = pyb.UART(DUP_PORT, DUP_SPEED)
uos.dupterm(termrep)
print('\n\r*** boot.py finished ***')
print('*** DUP_PORT@SPEED: {}@{} ***\n\r'.format(DUP_PORT, DUP_SPEED))
