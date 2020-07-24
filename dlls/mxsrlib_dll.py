from typing import Union
from os.path import dirname
from os import sep
import ctypes
from irspy.revisions import Revisions


def set_up_mxsrclib_dll(a_full_path):
    mx_dll = ctypes.CDLL(a_full_path)

    mx_dll.revision.restype = ctypes.c_int
    assert mx_dll.revision() == Revisions.mxsrlib_dll, f"Ревизия mxsrclib_dll не соответствует ожидаемой! " \
                                                       f"Текущая версия {mx_dll.revision()}. " \
                                                       f"Ожидаемая: {Revisions.mxsrlib_dll}"

    mx_dll.set_out_pins.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8]

    mx_dll.imp_filter_get.restype = ctypes.c_double

    mx_dll.student_t_inverse_distribution_2x.argtypes = [ctypes.c_double, ctypes.c_uint32]
    mx_dll.student_t_inverse_distribution_2x.restype = ctypes.c_double

    mx_dll.funnel_client_connected.restype = ctypes.c_int
    mx_dll.funnel_client_get.restype = ctypes.c_size_t
    mx_dll.is_read_complete.restype = ctypes.c_int
    mx_dll.funnel_client_get_read_size.restype = ctypes.c_int
    mx_dll.funnel_client_get_write_size.restype = ctypes.c_int

    return mx_dll


__path = dirname(__file__) + sep + "mxsrclib_dll.dll"
mxsrclib_dll: [Union, ctypes.CDLL] = set_up_mxsrclib_dll(__path)


class FunnelClient:
    def __init__(self):
        global mxsrclib_dll
        assert mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrclib_dll

        self.__created = False

    def create(self, a_mxdata, a_funnel_start_index, a_offset, a_size):
        if self.__created:
            self.destroy()

        self.mxsrclib_dll.funnel_client_create(a_mxdata, a_funnel_start_index, a_offset, a_size)

        self.__created = True

    def destroy(self):
        self.__created = False
        self.mxsrclib_dll.funnel_client_destroy()

    def connected(self) -> bool:
        if self.__created:
            return self.mxsrclib_dll.funnel_client_connected()
        else:
            return False

    def get_address(self):
        if self.__created:
            return self.mxsrclib_dll.funnel_client_get()
        else:
            return 0

    def tick(self):
        if self.__created:
            self.mxsrclib_dll.funnel_client_tick()

    def reset_stat_read_complete(self):
        if self.__created:
            self.mxsrclib_dll.funnel_client_reset_is_read_complete()

    def is_read_complete(self) -> bool:
        if self.__created:
            return self.mxsrclib_dll.is_read_complete()
        else:
            return False

    def get_read_size(self) -> int:
        if self.__created:
            return self.mxsrclib_dll.funnel_client_get_read_size()
        else:
            return 0

    def get_write_size(self) -> int:
        if self.__created:
            return self.mxsrclib_dll.funnel_client_get_write_size()
        else:
            return 0
