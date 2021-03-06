from os.path import dirname
from typing import Union
from os import sep
import logging
import ctypes
import enum

import irspy.clb.calibrator_constants as clb
from irspy.revisions import Revisions
import irspy.utils as utils


def set_up_driver(a_full_path):
    clb_driver_lib = ctypes.CDLL(a_full_path)

    clb_driver_lib.revision.restype = ctypes.c_int

    assert clb_driver_lib.revision() == Revisions.clb_dll, f"Ревизия clb_dll не соответствует ожидаемой! " \
                                                           f"Текущая версия {clb_driver_lib.revision()}. " \
                                                           f"Ожидаемая: {Revisions.clb_dll}"

    # Возвращает список калибраторов, разделенных ';'
    clb_driver_lib.get_usb_devices.restype = ctypes.c_char_p

    clb_driver_lib.connect_usb.argtypes = [ctypes.c_char_p]

    clb_driver_lib.set_amplitude.argtypes = [ctypes.c_double]
    clb_driver_lib.get_amplitude.restype = ctypes.c_double

    clb_driver_lib.set_frequency.argtypes = [ctypes.c_double]
    clb_driver_lib.get_frequency.restype = ctypes.c_double

    clb_driver_lib.set_signal_type.argtypes = [ctypes.c_int]
    clb_driver_lib.get_signal_type.restype = ctypes.c_int

    clb_driver_lib.set_polarity.argtypes = [ctypes.c_int]
    clb_driver_lib.get_polarity.restype = ctypes.c_int

    clb_driver_lib.signal_enable.argtypes = [ctypes.c_int]
    clb_driver_lib.enabled.restype = ctypes.c_int

    clb_driver_lib.get_usb_status.restype = ctypes.c_int
    clb_driver_lib.is_connected.restype = ctypes.c_int

    clb_driver_lib.set_mode.argtypes = [ctypes.c_int]
    clb_driver_lib.get_mode.restype = ctypes.c_int

    clb_driver_lib.is_signal_ready.restype = ctypes.c_int

    clb_driver_lib.fast_control_mode_enable.argtypes = [ctypes.c_int]

    clb_driver_lib.get_mxdata_address.restype = ctypes.c_size_t

    return clb_driver_lib


__path = dirname(__file__) + sep + "clb_driver_dll.dll"
clb_dll: [Union, ctypes.CDLL] = set_up_driver(__path)


class UsbDrv:
    class UsbState(enum.IntEnum):
        NOT_SUPPORTED = 0
        DISABLED = 1
        CONNECTED = 2
        BUSY = 3
        ERROR = 4

    def __init__(self, a_clb_dll, a_data_size):
        self.clb_dll = a_clb_dll
        # Обязательно перед любыми действиями с clb_driver_dll
        self.clb_dll.usb_init(a_data_size)

        self.clb_dev_list_changed = False
        self.clb_dev_list = []
        self.usb_status_changed = False
        self.usb_status = self.UsbState.DISABLED

    def tick(self):
        self.clb_dll.usb_tick()
        if self.clb_dll.usb_devices_changed():
            self.clb_dev_list.clear()

            clb_names_char = self.clb_dll.get_usb_devices()
            clb_names_list = clb_names_char.decode("ascii")

            for clb_name in clb_names_list.split(';'):
                if clb_name:
                    self.clb_dev_list.append(clb_name)
            self.clb_dev_list_changed = True

        usb_status = self.clb_dll.get_usb_status()
        if self.usb_status != usb_status:
            self.usb_status = usb_status
            self.usb_status_changed = True

    def is_status_changed(self):
        if self.usb_status_changed:
            self.usb_status_changed = False
            return True
        else:
            return False

    def is_dev_list_changed(self):
        if self.clb_dev_list_changed:
            self.clb_dev_list_changed = False
            return True
        else:
            return False

    def get_dev_list(self):
        return self.clb_dev_list

    def get_status(self):
        return self.UsbState(self.usb_status)


class ClbDrv:
    def __init__(self, a_clb_dll):
        self.__clb_dll = a_clb_dll

        self.__amplitude = 0
        self.__frequency = 0
        self.__signal_type = clb.SignalType.ACI
        self.__dc_polarity = clb.Polarity.POS
        self.__signal_on = False
        self.__mode = clb.Mode.SOURCE
        self.__signal_ready = False
        self.__state = clb.State.DISCONNECTED

        buf1_t = ctypes.c_char * 1
        buf2_t = ctypes.c_char * 2
        buf4_t = ctypes.c_char * 4
        buf8_t = ctypes.c_char * 8
        buf10_t = ctypes.c_char * 10

        self.__read_buffers = {
            1: buf1_t(),
            2: buf2_t(),
            4: buf4_t(),
            8: buf8_t(),
            10: buf10_t(),
        }

    def connect(self, a_clb_name: str):
        self.__amplitude = 0
        self.__frequency = 0
        self.__signal_type = clb.SignalType.ACI
        self.__dc_polarity = clb.Polarity.POS
        self.__signal_on = False
        self.__mode = clb.Mode.SOURCE
        self.__signal_ready = False
        self.__state = clb.State.DISCONNECTED

        if a_clb_name:
            self.__clb_dll.connect_usb(a_clb_name.encode("ascii"))
        else:
            self.__clb_dll.disconnect_usb()

    def amplitude_changed(self):
        actual_amplitude = clb.bound_amplitude(self.__clb_dll.get_amplitude(), self.__signal_type)
        signed_amplitude = actual_amplitude if self.__clb_dll.get_polarity() == clb.Polarity.POS else -actual_amplitude

        if self.__amplitude != signed_amplitude:
            self.__amplitude = signed_amplitude
            return True
        else:
            return False

    @property
    def amplitude(self):
        return self.__amplitude

    @amplitude.setter
    def amplitude(self, a_amplitude: float):
        amplitude = clb.bound_amplitude(a_amplitude, self.__signal_type)
        self.__clb_dll.set_amplitude(abs(amplitude))
        self.__set_polarity_by_amplitude_sign(amplitude)

    def limit_amplitude(self, a_amplitude, a_lower, a_upper):
        """
        Обрезает значение амплитуды с учетом типа сигнала и параметров пользователя
        :param a_amplitude: Заданная амплитуда
        :param a_lower: Нижняя граница
        :param a_upper: Верхняя граница
        """
        return utils.bound(clb.bound_amplitude(a_amplitude, self.__signal_type), a_lower, a_upper)

    def __set_polarity_by_amplitude_sign(self, a_amplitude):
        if a_amplitude < 0 and self.__clb_dll.get_polarity() != clb.Polarity.NEG:
            self.__clb_dll.set_polarity(clb.Polarity.NEG)
        elif a_amplitude >= 0 and self.__clb_dll.get_polarity() != clb.Polarity.POS:
            self.__clb_dll.set_polarity(clb.Polarity.POS)

    def frequency_changed(self):
        actual_frequency = utils.bound(self.__clb_dll.get_frequency(), clb.MIN_FREQUENCY, clb.MAX_FREQUENCY)
        if self.__frequency != actual_frequency:
            self.__frequency = actual_frequency
            return True
        else:
            return False

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, a_frequency: float):
        frequency = utils.bound(a_frequency, clb.MIN_FREQUENCY, clb.MAX_FREQUENCY)
        self.__clb_dll.set_frequency(frequency)

    def signal_type_changed(self):
        actual_signal_type = self.__clb_dll.get_signal_type()
        if self.__signal_type != actual_signal_type:
            self.__signal_type = actual_signal_type
            return True
        else:
            return False

    @property
    def signal_type(self):
        return self.__signal_type

    @signal_type.setter
    def signal_type(self, a_signal_type: int):
        self.__clb_dll.set_signal_type(a_signal_type)

    def is_signal_ready(self):
        return self.__clb_dll.is_signal_ready()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, a_state: clb.State):
        self.__state = a_state

    def signal_enable_changed(self):
        actual_enabled = self.__clb_dll.enabled()
        if self.__signal_on != actual_enabled:
            self.__signal_on = actual_enabled
            return True
        else:
            return False

    @property
    def signal_enable(self):
        return self.__signal_on

    @signal_enable.setter
    def signal_enable(self, a_signal_enable: int):
        self.__clb_dll.signal_enable(a_signal_enable)

    def mode_changed(self):
        actual_mode = self.__clb_dll.get_mode()
        if self.__mode != actual_mode:
            self.__mode = actual_mode
            return True
        else:
            return False

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, a_mode: int):
        self.__clb_dll.set_mode(a_mode)

    def fast_control_mode_enable(self, a_enable: int):
        self.__clb_dll.fast_control_mode_enable(a_enable)

    def read_raw_bytes(self, a_start_index: int, a_bytes_count: int):
        self.__clb_dll.read_bytes(self.__read_buffers[a_bytes_count], a_start_index, a_bytes_count)
        return self.__read_buffers[a_bytes_count]

    def write_raw_bytes(self, a_start_index: int, a_bytes_count: int, a_bytes):
        self.__clb_dll.write_bytes(a_bytes, a_start_index, a_bytes_count)

    def read_bit(self, a_byte_index: int, a_bit_index: int) -> int:
        return self.__clb_dll.read_bit(a_byte_index, a_bit_index)

    def write_bit(self, a_byte_index: int, a_bit_index: int, a_value: int):
        self.__clb_dll.write_bit(a_byte_index, a_bit_index, a_value)

    def get_mxdata_address(self) -> int:
        return self.__clb_dll.get_mxdata_address()
