# -*- coding: utf-8 -*-
"""
RED LED: exception during processing of ubx_msg
GREEN LED: exception during rh update or write to buffer

Serial port pins:
Ser 1:    Rx X10      Tx X9
Ser 2:    Rx X4       Tx X3
Ser 3:    Rx Y10      Tx Y9 (USED FOR DUPTERM!)
Ser 4:    Rx X2       Tx X1
Ser 6:    Rx Y2       Tx Y1
"""
import sys
from time import sleep

import pyb

from outputs import FileWriter
from outputs import OutputBuffer
from rel_heading import RelativeHeading
from ubx import UbxDataBuffer
from ubx import UbxMsg

MAX_BUFF_LENGTH = 256 # max number of bytes in the processing buffer
SER_ROVER_PORT = 4
SER_OUT_PORT = 2
SER_ROVER_SPEED = 38400
SER_OUT_SPEED = 9600
OUTPUT_FILE = 'output.csv'
OUTPUT_FILE_BUFFER_SIZE = 100

def init_ser():
    ser_rover = pyb.UART(SER_ROVER_PORT, SER_ROVER_SPEED, read_buf_len=256)
    ser_output = pyb.UART(SER_OUT_PORT, SER_OUT_SPEED)
    # ser_out.write('INIT SER{} @{} baud\r\n'.format(SER_OUT_PORT, SER_OUT_SPEED))
    print('INIT SER{} @{} baud\r\n'.format(SER_OUT_PORT, SER_OUT_SPEED))
    return ser_rover, ser_output

def init_hw():
    ledGreen = pyb.LED(2)
    ledRed = pyb.LED(1)
    return ledGreen, ledRed

def init_other():
    data_buff = UbxDataBuffer(MAX_BUFF_LENGTH)  # buffer for incoming serial rover data
    rh = RelativeHeading()  # calculates/updates the relative heading
    output_buff = OutputBuffer()  # holds the data that will be send to the function for output
    filewriter = FileWriter(outputfile = OUTPUT_FILE, buffersize = OUTPUT_FILE_BUFFER_SIZE)
    sleep(0.5)      # sleep for 500 milliseconds, not sure if needed(?)
    return data_buff, rh, output_buff, filewriter

def main():
    ser_rover, ser_output = init_ser()
    ledGreen, ledRed = init_hw()
    data_buff, rh, output_buff, filewriter = init_other()

    while True:
        if ser_rover.any()>0:  # received data
            data_buff.add(ser_rover.read(MAX_BUFF_LENGTH))  # get the data and put in the buffer

            next_msg = data_buff.return_first_msg()  # take the first msg out of the buffer (if found)
            if next_msg:

                # handle and process the next_msg as a ubx message
                try:
                    m = UbxMsg(next_msg)  # use the msg
                    processed_msg = m.process()  # and process

                    if not processed_msg['ok']:
                        err = 'Issue during processing of message: {}'.format(processed_msg['err_msg'])
                        raise Exception(err)


                except Exception as e:
                    ledGreen.toggle()
                    sys.print_exception(e)
                    # ser_out.write('Green exception (rh update or write to buffer): {}'.format(e))
                    print('Green exception (rh update or write to buffer): {}'.format(e))

                finally:
                    #update screen
                    pass



if __name__ == '__main__':
    main()
