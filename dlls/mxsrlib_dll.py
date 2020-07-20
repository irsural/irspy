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

    return mx_dll


__path = dirname(__file__) + sep + "mxsrclib_dll.dll"
mxsrclib_dll: [Union, ctypes.CDLL] = set_up_mxsrclib_dll(__path)
