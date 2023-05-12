# -*- coding: utf-8 -*-
class MovingAvg:

    __all__ = ('reset', 'update')
    def __init__(self, size):
        self._size = size
        self.result = None
        self._array = []

    def reset(self):
        self._array = []
        self.result = None

    def _calculate_result(self):
        self.result = sum(self._array)/self._size

    def update(self, value):
        self._array.append(value)
        arraylength = len(self._array)
        if arraylength < self._size:
            return False

        if arraylength > self._size:
            self._array = self._array[-self._size:]

        if len(self._array) == self._size:
            self._calculate_result()
            return True

        return False
