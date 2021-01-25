from typing import Union
from array import array
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

    mx_dll.ftdi_set_out_pins.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8]
    mx_dll.ftdi_reinit.restype = ctypes.c_int
    mx_dll.ftdi_write_gpio.argtypes = [ctypes.c_uint32, ctypes.c_uint8, ctypes.c_int]
    mx_dll.ftdi_write_gpio.restype = ctypes.c_int
    mx_dll.ftdi_read_gpio.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8]
    mx_dll.ftdi_read_gpio.restype = ctypes.c_int
    mx_dll.ftdi_write_byte.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8]
    mx_dll.ftdi_write_byte.restype = ctypes.c_int

    mx_dll.imp_filter_get.restype = ctypes.c_double

    mx_dll.student_t_inverse_distribution_2x.argtypes = [ctypes.c_double, ctypes.c_uint32]
    mx_dll.student_t_inverse_distribution_2x.restype = ctypes.c_double

    mx_dll.funnel_client_connected.restype = ctypes.c_int
    mx_dll.funnel_client_get.restype = ctypes.c_size_t
    mx_dll.is_read_complete.restype = ctypes.c_int
    mx_dll.funnel_client_get_read_size.restype = ctypes.c_int
    mx_dll.funnel_client_get_write_size.restype = ctypes.c_int

    mx_dll.correct_map_create.restype = ctypes.c_uint32
    mx_dll.correct_map_destroy.restype = ctypes.c_uint32
    mx_dll.correct_map_get_x_points_count.restype = ctypes.c_uint32
    mx_dll.correct_map_get_y_points_count.restype = ctypes.c_uint32
    mx_dll.correct_map_get_coef_points_count.restype = ctypes.c_uint32
    mx_dll.correct_map_get_x_points.restype = ctypes.c_int
    mx_dll.correct_map_get_y_points.restype = ctypes.c_int
    mx_dll.correct_map_get_coefs_points.restype = ctypes.c_int
    mx_dll.correct_map_connect.restype = ctypes.c_int

    mx_dll.connect_to_agilent_3458a.argtypes = [ctypes.c_size_t, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int,
                                                ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p]
    mx_dll.connect_to_agilent_3458a.restype = ctypes.c_int

    mx_dll.multimeter_start_measure.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
    mx_dll.multimeter_start_measure.restype = ctypes.c_int

    mx_dll.multimeter_get_status.restype = ctypes.c_int
    mx_dll.multimeter_get_status.restype = ctypes.c_int
    mx_dll.multimeter_set_config.artypes = [ctypes.c_size_t, ctypes.c_char_p]

    mx_dll.param_filter_add.argtypes = [ctypes.c_double]
    mx_dll.param_filter_set_sampling_time.argtypes = [ctypes.c_double]
    mx_dll.param_filter_resize.argtypes = [ctypes.c_size_t]
    mx_dll.param_filter_get_value.restype = ctypes.c_double

    mx_dll.multimeter_set_range.argtypes = [ctypes.c_size_t, ctypes.c_double]

    mx_dll.pchip_set_points.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_double),
                                        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
    mx_dll.pchip_interpolate.argtypes = [ctypes.c_size_t, ctypes.c_double]
    mx_dll.pchip_interpolate.restype = ctypes.c_double
    mx_dll.pchip_destroy.argtypes = [ctypes.c_size_t]

    return mx_dll


__path = dirname(__file__) + sep + "mxsrclib_dll.dll"
mxsrclib_dll: [Union, ctypes.CDLL] = set_up_mxsrclib_dll(__path)


class FunnelClient:
    def __init__(self):
        global mxsrclib_dll
        assert mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrclib_dll

        self.__data_size = 0
        self.__created = False

    def __del__(self):
        if self.__created:
            self.destroy()

    def create(self, a_mxdata, a_funnel_start_index, a_offset, a_size):
        if self.__created:
            self.destroy()

        self.mxsrclib_dll.funnel_client_create(a_mxdata, a_funnel_start_index, a_offset, a_size)

        self.__data_size = a_size
        self.__created = True

    def destroy(self):
        self.__created = False
        self.__data_size = 0
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

    def data_size(self):
        return self.__data_size

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


class CorrectMap:
    def __init__(self):
        global mxsrclib_dll
        assert mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrclib_dll

        self.__handle = 0

        self.__x_points = None
        self.__y_points = None
        self.__coefs_points = None

        self.__created = False

    def __del__(self):
        if self.__created:
            self.destroy()

    def create(self):
        if self.__created:
            self.destroy()
        self.__handle = self.mxsrclib_dll.correct_map_create()
        self.__created = True

    def destroy(self):
        self.mxsrclib_dll.correct_map_destroy(self.__handle)
        self.__x_points = None
        self.__y_points = None
        self.__coefs_points = None
        self.__created = False

    def connect(self, a_mxdata_address: int):
        assert self.__created, "CorrectMap не подклюена!"

        self.mxsrclib_dll.correct_map_connect(self.__handle, a_mxdata_address)

    def get_x_points_count(self):
        return self.mxsrclib_dll.correct_map_get_x_points_count(self.__handle)

    def get_y_points_count(self):
        return self.mxsrclib_dll.correct_map_get_y_points_count(self.__handle)

    def set_x_points_count(self, a_points_count):
        self.mxsrclib_dll.correct_map_set_x_points_count(self.__handle, a_points_count)

    def set_y_points_count(self, a_points_count):
        self.mxsrclib_dll.correct_map_set_y_points_count(self.__handle, a_points_count)

    @property
    def x_points(self):
        assert self.__created, "CorrectMap не подклюена!"

        x_count = self.mxsrclib_dll.correct_map_get_x_points_count(self.__handle)
        self.__x_points = (ctypes.c_double * x_count)()

        self.mxsrclib_dll.correct_map_get_x_points(self.__handle, self.__x_points)
        return list(self.__x_points)

    @x_points.setter
    def x_points(self, a_points: array):
        assert self.__created, "CorrectMap не подклюена!"

        address, size = a_points.buffer_info()
        pointer_to_double = ctypes.cast(address, ctypes.POINTER(ctypes.c_double))

        self.mxsrclib_dll.correct_map_set_x_points(self.__handle, pointer_to_double, size)

    @property
    def y_points(self):
        assert self.__created, "CorrectMap не подклюена!"

        y_count = self.mxsrclib_dll.correct_map_get_y_points_count(self.__handle)
        self.__y_points = (ctypes.c_double * y_count)()

        self.mxsrclib_dll.correct_map_get_y_points(self.__handle, self.__y_points)
        return list(self.__y_points)

    @y_points.setter
    def y_points(self, a_points: array):
        assert self.__created, "CorrectMap не подклюена!"

        address, size = a_points.buffer_info()
        pointer_to_double = ctypes.cast(address, ctypes.POINTER(ctypes.c_double))

        self.mxsrclib_dll.correct_map_set_y_points(self.__handle, pointer_to_double, size)

    @property
    def coef_points(self):
        assert self.__created, "CorrectMap не подклюена!"

        coefs_count = self.mxsrclib_dll.correct_map_get_coef_points_count(self.__handle)
        self.__coefs_points = (ctypes.c_double * coefs_count)()

        self.mxsrclib_dll.correct_map_get_coefs_points(self.__handle, self.__coefs_points)
        return list(self.__coefs_points)

    @coef_points.setter
    def coef_points(self, a_points: array):
        assert self.__created, "CorrectMap не подклюена!"

        address, size = a_points.buffer_info()
        pointer_to_double = ctypes.cast(address, ctypes.POINTER(ctypes.c_double))

        self.mxsrclib_dll.correct_map_set_coef_points(self.__handle, pointer_to_double, size)
