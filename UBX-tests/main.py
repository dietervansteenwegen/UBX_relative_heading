# -*- coding: utf-8 -*-
import pyb
from u_msg_ubx import msg_ubx

ser1 = pyb.UART(1,38400, read_buf_len = 256)
# ser2 = pyb.UART(2,115200, read_buf_len = 256)

while True:
    RxBuffCnt = ser1.any()
    if RxBuffCnt:
        RxBuff = ser1.read(RxBuffCnt)

m=b''
i=0
while i <10:
    if ser1.any():
        m += ser1.read()
        i += 1

hex(int.from_bytes(m[:], 'big'))
