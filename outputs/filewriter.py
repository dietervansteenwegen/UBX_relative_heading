# -*- coding: utf-8 -*-
class FileWriter():

    def __init__(self, outputfile = 'output.txt', buffersize = 20, line_end = '\r\n'):
        self._outputfile = outputfile
        self._buffersize = buffersize
        self._line_end = line_end
        self._buffer = []

    def flush(self):
        try:
            with open(self._outputfile, 'a') as f:
                for l in self._buffer:
                    f.write(l + self._line_end)
            self._buffer = []
        except Exception as e:  # filesystem may be full
            print('Error {}, flushing buffer without write'.format(e))  # if e == 28 then file system is full
            self._buffer = []

    def add(self, msg):
        self._buffer.append(msg.strip())
        if len(self._buffer) >= self._buffersize:
            self.flush()
