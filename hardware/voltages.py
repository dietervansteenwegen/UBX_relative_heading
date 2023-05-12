# -*- coding: utf-8 -*-
import pyb

BATT_SCALING = 2  # conversion multiplier from pin voltage to voltage divider input
VCC_SCALING = 2  # conversion multiplier from pin voltage to voltage divider input


class Voltages:
    """" Read and convert voltages from the two resistor dividers.
    Vcc is connected to pin X11, battery to X12.
    """

    def __init__(self):
        vcc_raw_pin = pyb.Pin(pyb.Pin.board.X11, pyb.Pin.IN)
        self.vcc_raw = pyb.ADC(vcc_raw_pin)
        bat_raw_pin = pyb.Pin(pyb.Pin.board.X12, pyb.Pin.IN)
        self.bat_raw = pyb.ADC(bat_raw_pin)
        self._vcc_raw_counts = 0
        self._bat_raw_counts = 0
        self.vcc_converted = 0
        self.bat_converted = 0

    def _get_raw_counts(self):
        """ Get raw counts for both ADC inputs.
        Range = 0 to 4095 counts.
        Reference is 3.3V from on-board LDO
        """
        self._vcc_raw_counts = self.vcc_raw.read()
        self._bat_raw_counts = self.bat_raw.read()

    def _convert_from_raw(self):
        """ Apply scaling to the raw counts.
        Raw count range is (0,4095) for (0V,3.3V) input.
        Scaling to raw input voltage: raw count /(4095*3.3)
        Then scale for voltage divider using the two constants.
        """
        vcc_input = (self._vcc_raw_counts*3.3)/4095
        bat_input = (self._bat_raw_counts*3.3)/4095
        self.vcc_converted = vcc_input * VCC_SCALING
        self.bat_converted = bat_input * BATT_SCALING

    def get_voltages(self):
        self._get_raw_counts()
        self._convert_from_raw()
        return self.vcc_converted, self.bat_converted
