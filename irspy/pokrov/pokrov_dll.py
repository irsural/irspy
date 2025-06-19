from os.path import dirname
from typing import Union
from os import sep
import ipaddress
import logging
import ctypes

from irspy.revisions import Revisions


def set_up_driver(a_full_path):
    pokrov_dll_lib = ctypes.CDLL(a_full_path)

    pokrov_dll_lib.revision.restype = ctypes.c_int

    assert pokrov_dll_lib.revision() == Revisions.pokrov_dll, f"Ревизия pokrov_dll не соответствует ожидаемой! " \
                                                              f"Текущая версия {pokrov_dll_lib.revision()}. " \
                                                              f"Ожидаемая: {Revisions.pokrov_dll}"

    pokrov_dll_lib.gnrw_connect.argtypes = [ctypes.c_char_p]

    pokrov_dll_lib.is_gnrw_connected.restype = ctypes.c_size_t

    pokrov_dll_lib.signal_on.argtypes = [ctypes.c_int]

    pokrov_dll_lib.get_id.restype = ctypes.c_size_t

    pokrov_dll_lib.set_ether_power.argtypes = [ctypes.c_size_t]
    pokrov_dll_lib.get_ether_power.restype = ctypes.c_size_t

    pokrov_dll_lib.set_line_power.argtypes = [ctypes.c_size_t]
    pokrov_dll_lib.get_line_power.restype = ctypes.c_size_t

    return pokrov_dll_lib


__path = dirname(__file__) + sep + "pokrov_dll.dll"
_pokrov_dll: [Union, ctypes.CDLL] = set_up_driver(__path)


class PokrovDrv:
    def __init__(self):
        global _pokrov_dll
        self.__pokrov_dll = _pokrov_dll
        self.__pokrov_dll.init()

    def connect(self, a_ip: str):
        try:
            ipaddress.ip_address(a_ip)
        except ValueError:
            logging.error(f"PokrovDrv.connect({a_ip}) - невалидный ip-адрес")
        else:
            self.__pokrov_dll.gnrw_connect(a_ip.encode("ascii"))

    def is_connected(self):
        return bool(self.__pokrov_dll.is_gnrw_connected())

    def tick(self):
        self.__pokrov_dll.tick()

    def signal_on(self, a_enable):
        if self.is_connected():
            self.__pokrov_dll.signal_on(a_enable)

    @property
    def id(self):
        if self.is_connected():
            return self.__pokrov_dll.get_id()
        else:
            return 0

    @property
    def ether_power(self):
        if self.is_connected():
            return self.__pokrov_dll.get_ether_power()
        else:
            return 0

    @ether_power.setter
    def ether_power(self, a_value: float):
        if self.is_connected():
            self.__pokrov_dll.set_ether_power(a_value)

    @property
    def line_power(self):
        if self.is_connected():
            return self.__pokrov_dll.get_line_power()
        else:
            return 0

    @line_power.setter
    def line_power(self, a_value: float):
        if self.is_connected():
            self.__pokrov_dll.set_line_power(a_value)
