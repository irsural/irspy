from os.path import dirname
from typing import Union
from os import sep
import ipaddress
import logging
import ctypes
import sys

from irspy.revisions import Revisions


def set_up_driver(a_full_path) -> [Union, ctypes.CDLL]:
    pokrov_dll_lib = ctypes.CDLL(a_full_path)

    pokrov_dll_lib.revision.restype = ctypes.c_int
    pokrov_dll_lib.mem_used.restype = ctypes.c_double

    assert pokrov_dll_lib.revision() == Revisions.pokrov_dll, \
        "Ревизия pokrov_dll не соответствует ожидаемой! Текущая версия {}. Ожидаемая: {}".format(
        pokrov_dll_lib.revision(), Revisions.pokrov_dll)

    pokrov_dll_lib.create.restype = ctypes.c_size_t
    pokrov_dll_lib.destroy.argtypes = [ctypes.c_size_t]

    pokrov_dll_lib.tick.argtypes = [ctypes.c_size_t]

    pokrov_dll_lib.gnrw_connect.argtypes = [ctypes.c_size_t, ctypes.c_char_p]

    pokrov_dll_lib.is_gnrw_connected.argtypes = [ctypes.c_size_t]
    pokrov_dll_lib.is_gnrw_connected.restype = ctypes.c_size_t

    pokrov_dll_lib.signal_on.argtypes = [ctypes.c_size_t, ctypes.c_int]
    pokrov_dll_lib.is_signal_on.argtypes = [ctypes.c_int]
    pokrov_dll_lib.is_signal_on.restype = ctypes.c_int

    pokrov_dll_lib.is_fault.argtypes = [ctypes.c_int]
    pokrov_dll_lib.is_fault.restype = ctypes.c_int
    pokrov_dll_lib.is_ether_ok.argtypes = [ctypes.c_int]
    pokrov_dll_lib.is_ether_ok.restype = ctypes.c_int
    pokrov_dll_lib.is_line_ok.argtypes = [ctypes.c_int]
    pokrov_dll_lib.is_line_ok.restype = ctypes.c_int

    pokrov_dll_lib.get_work_time.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_work_time.restype = ctypes.c_double
    pokrov_dll_lib.get_ether_work_time.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_ether_work_time.restype = ctypes.c_double
    pokrov_dll_lib.get_line_work_time.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_line_work_time.restype = ctypes.c_double

    pokrov_dll_lib.get_id.argtypes = [ctypes.c_size_t]
    pokrov_dll_lib.get_id.restype = ctypes.c_size_t

    pokrov_dll_lib.set_ether_power.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
    pokrov_dll_lib.get_ether_power.argtypes = [ctypes.c_size_t]
    pokrov_dll_lib.get_ether_power.restype = ctypes.c_size_t

    pokrov_dll_lib.set_line_power.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
    pokrov_dll_lib.get_line_power.argtypes = [ctypes.c_size_t]
    pokrov_dll_lib.get_line_power.restype = ctypes.c_size_t

    pokrov_dll_lib.get_volume.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_volume.restype = ctypes.c_size_t

    pokrov_dll_lib.get_brightness.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_brightness.restype = ctypes.c_size_t

    pokrov_dll_lib.get_show_power_interval.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_show_power_interval.restype = ctypes.c_size_t
    pokrov_dll_lib.get_show_time_interval.argtypes = [ctypes.c_int]
    pokrov_dll_lib.get_show_time_interval.restype = ctypes.c_size_t

    return pokrov_dll_lib


__dll_name = "pokrov_dll_64.dll" if sys.maxsize > 2**32 else "pokrov_dll_32.dll"
__path = dirname(__file__) + sep + __dll_name
_pokrov_dll = set_up_driver(__path)


class PokrovDrv:
    def __init__(self):
        global _pokrov_dll
        self.__pokrov_dll = _pokrov_dll
        self.__pokrov_handle = self.__pokrov_dll.create()
        self.__ip = "0.0.0.0"

    def __del__(self):
        self.__pokrov_dll.destroy(self.__pokrov_handle)

    def connect(self, a_ip: str):
        try:
            ipaddress.ip_address(a_ip)
        except ValueError:
            logging.error("PokrovDrv.connect({}) - невалидный ip-адрес".format(a_ip))
        else:
            self.__ip = a_ip
            self.__pokrov_dll.gnrw_connect(self.__pokrov_handle, a_ip.encode("ascii"))

    def get_ip(self):
        return self.__ip

    def is_connected(self):
        return bool(self.__pokrov_dll.is_gnrw_connected(self.__pokrov_handle))

    def tick(self):
        self.__pokrov_dll.tick(self.__pokrov_handle)

    def is_signal_on(self):
        signal_on = False
        if self.is_connected():
            signal_on = self.__pokrov_dll.is_signal_on(self.__pokrov_handle)
        return signal_on

    def signal_on(self, a_enable):
        if self.is_connected():
            self.__pokrov_dll.signal_on(self.__pokrov_handle, a_enable)

    def is_fault(self):
        fault = False
        if self.is_connected():
            fault = self.__pokrov_dll.is_fault(self.__pokrov_handle)
        return fault

    def is_ether_ok(self):
        ether_ok = False
        if self.is_connected():
            ether_ok = self.__pokrov_dll.is_ether_ok(self.__pokrov_handle)
        return ether_ok

    def is_line_ok(self):
        line_ok = False
        if self.is_connected():
            line_ok = self.__pokrov_dll.is_line_ok(self.__pokrov_handle)
        return line_ok

    def work_time(self):
        work_time = 0
        if self.is_connected():
            work_time = self.__pokrov_dll.get_work_time(self.__pokrov_handle)
        return work_time

    def ether_work_time(self):
        ether_work_time = 0
        if self.is_connected():
            ether_work_time = self.__pokrov_dll.get_ether_work_time(self.__pokrov_handle)
        return ether_work_time

    def line_work_time(self):
        line_work_time = 0
        if self.is_connected():
            line_work_time = self.__pokrov_dll.get_line_work_time(self.__pokrov_handle)
        return line_work_time

    @property
    def id(self):
        if self.is_connected():
            return self.__pokrov_dll.get_id(self.__pokrov_handle)
        else:
            return 0

    @property
    def ether_power(self):
        if self.is_connected():
            return self.__pokrov_dll.get_ether_power(self.__pokrov_handle)
        else:
            return 0

    @ether_power.setter
    def ether_power(self, a_value: float):
        if self.is_connected():
            self.__pokrov_dll.set_ether_power(self.__pokrov_handle, a_value)

    @property
    def line_power(self):
        if self.is_connected():
            return self.__pokrov_dll.get_line_power(self.__pokrov_handle)
        else:
            return 0

    @line_power.setter
    def line_power(self, a_value: float):
        if self.is_connected():
            self.__pokrov_dll.set_line_power(self.__pokrov_handle, a_value)

    def volume(self):
        volume = 0
        if self.is_connected():
            volume = self.__pokrov_dll.get_volume(self.__pokrov_handle)
        return volume

    def brightness(self):
        brightness = 0
        if self.is_connected():
            brightness = self.__pokrov_dll.get_brightness(self.__pokrov_handle)
        return brightness

    def show_power_interval(self):
        show_power_interval = 0
        if self.is_connected():
            show_power_interval = self.__pokrov_dll.get_show_power_interval(self.__pokrov_handle)
        return show_power_interval

    def show_time_interval(self):
        show_time_interval = 0
        if self.is_connected():
            show_time_interval = self.__pokrov_dll.get_show_time_interval(self.__pokrov_handle)
        return show_time_interval
