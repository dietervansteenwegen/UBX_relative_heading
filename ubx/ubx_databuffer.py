# -*- coding: utf-8 -*-
class UbxDataBuffer:

    def __init__(self,max_size = 256):
        self.max_size = max_size
        self.buff = b''
        self.size = 20*[0]
        self.avg_size = 0

    def add(self, buff):
        if len(self.buff) > self.max_size:
            self.buff = b''
        self.buff += buff

    def return_first_msg(self):
        start = self.buff.find(b'\xB5\x62')
        if start >= 0:
            stop = self.buff.find(b'\xB5\x62', start+2)
            if stop > start:
                ret = self.buff[start:stop]
                self.buff = self.buff[stop:]
                self.update_size()
                return ret
        return None

    def update_size(self):
        self.size[0:19] = self.size[1:]
        self.size[19] = len(self.buff)
        self.avg_size=0
        for i in self.size:
            self.avg_size += i
        self.avg_size = self.avg_size/20
