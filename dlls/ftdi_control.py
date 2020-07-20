from collections import namedtuple
from enum import IntEnum
import logging

from irspy.dlls import mxsrlib_dll

FtdiPin = namedtuple("FtdiPin", "channel bus pin")


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

    def __init__(self):
        assert mxsrlib_dll.mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrlib_dll.mxsrclib_dll

        self.pin_buffers = {
            (FtdiControl.Channel.A, FtdiControl.Bus.D): 0b00000000,
            (FtdiControl.Channel.A, FtdiControl.Bus.C): 0b00000000,
            (FtdiControl.Channel.B, FtdiControl.Bus.D): 0b00000000,
            (FtdiControl.Channel.B, FtdiControl.Bus.C): 0b00000000,
        }

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

    def is_connected(self) -> bool:
        return True

    def set_pin(self, a_ftdi_pin: FtdiPin, a_state: bool):
        if a_state:
            self.pin_buffers[(a_ftdi_pin.channel, a_ftdi_pin.bus)] |= a_ftdi_pin.pin
        else:
            self.pin_buffers[(a_ftdi_pin.channel, a_ftdi_pin.bus)] &= ~a_ftdi_pin.pin

    def __write_byte(self, a_channel: Channel, a_bus: Bus, a_byte: int) -> bool:
        # self.mxsrclib_dll.write_byte(a_channel, a_bus, a_byte)
        return True

    def write_changes(self) -> bool:
        pins_ok = []
        for (channel, bus), pins in self.pin_buffers.items():
            result = self.__write_byte(channel, bus, pins)
            pins_ok.append(result)

        return all(pins_ok)
