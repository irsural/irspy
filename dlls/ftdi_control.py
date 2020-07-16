from enum import IntEnum
import logging


class FtdiControl:
    class Channel(IntEnum):
        A = 0
        B = 1

    class Bus(IntEnum):
        D = 0
        C = 1

    class Pin(IntEnum):
        _0 = 0b00000001
        _1 = 0b00000010
        _2 = 0b00000100
        _3 = 0b00001000
        _4 = 0b00010000
        _5 = 0b00100000
        _6 = 0b01000000
        _7 = 0b10000000
        ALL = 0b11111111

    def __init__(self, a_mxsrclib):
        self.mxsrclib_dll = a_mxsrclib
        self.reinit()

    def set_out_pins(self, a_channel: Channel, a_bus: Bus, a_pins: int):
        self.mxsrclib_dll.set_out_pins(a_channel, a_bus, int(a_pins))

    def write_gpio(self, a_channel: Channel, a_bus: Bus, a_pins: int, a_state: bool) -> bool:
        return bool(self.mxsrclib_dll.write_gpio(a_channel, a_bus, int(a_pins), int(a_state)))

    def read_gpio(self, a_channel: Channel, a_bus: Bus, a_pins: int):
        return self.mxsrclib_dll.read_gpio(a_channel, a_bus, int(a_pins))

    def reinit(self):
        self.mxsrclib_dll.reinit()

        result = True

        self.mxsrclib_dll.set_out_pins(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin.ALL)
        if not self.mxsrclib_dll.write_gpio(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin.ALL, False):
            result = False

        self.mxsrclib_dll.set_out_pins(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin.ALL)
        if not self.mxsrclib_dll.write_gpio(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin.ALL, False):
            result = False

        self.mxsrclib_dll.set_out_pins(FtdiControl.Channel.B, FtdiControl.Bus.D,
                                       FtdiControl.Pin._4 | FtdiControl.Pin._5 | FtdiControl.Pin._6)
        if not self.mxsrclib_dll.write_gpio(FtdiControl.Channel.B, FtdiControl.Bus.D, FtdiControl.Pin.ALL, False):
            result = False

        self.mxsrclib_dll.set_out_pins(FtdiControl.Channel.B, FtdiControl.Bus.C, FtdiControl.Pin.ALL & ~FtdiControl.Pin._0)
        if not self.mxsrclib_dll.write_gpio(FtdiControl.Channel.B, FtdiControl.Bus.C, FtdiControl.Pin.ALL, False):
            result = False

        return result
