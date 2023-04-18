from collections import namedtuple
from enum import IntEnum
import logging
import ctypes

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
            # После инициализации ftdi все пины установлены в 1
            (FtdiControl.Channel.A, FtdiControl.Bus.D): 0b11111111,
            (FtdiControl.Channel.A, FtdiControl.Bus.C): 0b11111111,
            (FtdiControl.Channel.B, FtdiControl.Bus.D): 0b11111111,
            (FtdiControl.Channel.B, FtdiControl.Bus.C): 0b01111111,
        }

        self.pin_changed = {
            (FtdiControl.Channel.A, FtdiControl.Bus.D): False,
            (FtdiControl.Channel.A, FtdiControl.Bus.C): False,
            (FtdiControl.Channel.B, FtdiControl.Bus.D): False,
            (FtdiControl.Channel.B, FtdiControl.Bus.C): False,
        }

    def set_out_pins(self, a_channel: Channel, a_bus: Bus, a_pins: int):
        self.mxsrclib_dll.ftdi_set_out_pins(a_channel, a_bus, int(a_pins))

    def write_gpio(self, a_channel: Channel, a_bus: Bus, a_pins: int, a_state: bool) -> bool:
        return bool(self.mxsrclib_dll.ftdi_write_gpio(a_channel, a_bus, int(a_pins), int(a_state)))

    def read_gpio(self, a_channel: Channel, a_bus: Bus, a_pins: int):
        return self.mxsrclib_dll.ftdi_read_gpio(a_channel, a_bus, int(a_pins))

    def __write_byte(self, a_channel: Channel, a_bus: Bus, a_byte: int) -> bool:
        return bool(self.mxsrclib_dll.ftdi_write_byte(a_channel, a_bus, ctypes.c_uint8(a_byte)))

    def reinit(self):
        result = False

        if self.mxsrclib_dll.ftdi_reinit():

            self.mxsrclib_dll.ftdi_set_out_pins(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin.ALL)
            self.set_pin(FtdiPin(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin.ALL), False)

            self.mxsrclib_dll.ftdi_set_out_pins(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin.ALL)
            self.set_pin(FtdiPin(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin.ALL), False)

            self.mxsrclib_dll.ftdi_set_out_pins(FtdiControl.Channel.B, FtdiControl.Bus.D, FtdiControl.Pin.ALL)
            self.set_pin(FtdiPin(FtdiControl.Channel.B, FtdiControl.Bus.D, FtdiControl.Pin.ALL), False)

            self.mxsrclib_dll.ftdi_set_out_pins(FtdiControl.Channel.B, FtdiControl.Bus.C, FtdiControl.Pin.ALL & ~FtdiControl.Pin._7)
            self.set_pin(FtdiPin(FtdiControl.Channel.B, FtdiControl.Bus.C, FtdiControl.Pin.ALL & ~FtdiControl.Pin._7  & ~FtdiControl.Pin._6), False)

            if self.write_changes():
                # Включаем Enable, после того, как опустили все пины в 0
                self.set_pin(FtdiPin(FtdiControl.Channel.B, FtdiControl.Bus.C, FtdiControl.Pin._6), False)
                if self.write_changes():
                    result = True

        return result

    def is_connected(self) -> bool:
        result = False

        if self.write_gpio(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin._6, True):
            if self.write_gpio(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin._6, False):
                result = True

        return result

    def set_pin(self, a_ftdi_pin: FtdiPin, a_state: bool):
        if a_state:
            self.pin_buffers[(a_ftdi_pin.channel, a_ftdi_pin.bus)] |= a_ftdi_pin.pin
        else:
            self.pin_buffers[(a_ftdi_pin.channel, a_ftdi_pin.bus)] &= ~a_ftdi_pin.pin

        self.pin_changed[(a_ftdi_pin.channel, a_ftdi_pin.bus)] = True

    def write_changes(self) -> bool:
        pins_ok = []
        for (channel, bus), pins in self.pin_buffers.items():
            if self.pin_changed[(channel, bus)]:
                # logging.debug(f"write_changes: {channel.name}::{bus.name} write: {pins:>08b}")

                result = self.__write_byte(channel, bus, pins)
                if result:
                    self.pin_changed[(channel, bus)] = False
            else:
                result = True

            pins_ok.append(result)
        return all(pins_ok)


if __name__ == "__main__":
    import time

    ftdi = FtdiControl()
    if not ftdi.is_connected():
        print("not connected")
        if ftdi.reinit():
            print("success reinit")
            if ftdi.is_connected():

                ftdi.set_pin(FtdiPin(FtdiControl.Channel.B, FtdiControl.Bus.C, FtdiControl.Pin.ALL & ~FtdiControl.Pin._6 & ~FtdiControl.Pin._7), True)
                if ftdi.write_changes():
                    time.sleep(2)

                ftdi.set_pin(FtdiPin(FtdiControl.Channel.A, FtdiControl.Bus.C, FtdiControl.Pin.ALL), True)
                if ftdi.write_changes():
                    time.sleep(2)

                ftdi.set_pin(FtdiPin(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin.ALL), True)
                if ftdi.write_changes():
                    time.sleep(2)

                ftdi.set_pin(FtdiPin(FtdiControl.Channel.B, FtdiControl.Bus.D, FtdiControl.Pin.ALL), True)
                if ftdi.write_changes():
                    time.sleep(2)

    print("done")
