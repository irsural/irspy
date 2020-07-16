from typing import Union
import ctypes

mxsrclib_dll: [Union, ctypes.CDLL] = None


def set_up_mxsrclib_dll(a_full_path):
    global mxsrclib_dll
    mxsrclib_dll = ctypes.CDLL(a_full_path)

    mxsrclib_dll.set_out_pins.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8]

    mxsrclib_dll.imp_filter_get.restype = ctypes.c_double

    mxsrclib_dll.student_t_inverse_distribution_2x.argtypes = [ctypes.c_double, ctypes.c_uint32]
    mxsrclib_dll.student_t_inverse_distribution_2x.restype = ctypes.c_double
