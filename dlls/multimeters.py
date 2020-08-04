from enum import IntEnum
import ctypes

from irspy.dlls import mxsrlib_dll


# Из mxsrclib -> measmul.h
class MeasureType(IntEnum):
    tm_value = 1
    tm_volt_dc = 2,
    tm_volt_ac = 3,
    tm_current_dc = 4,
    tm_current_ac = 5,
    tm_resistance_2x = 6,
    tm_resistance_4x = 7,
    tm_frequency = 8,
    tm_phase = 9,
    tm_phase_average = 10,
    tm_time_interval = 11,
    tm_time_interval_average = 12,
    tm_distortion = 13,


class Agilent3485A:
    def __init__(self):
        assert mxsrlib_dll.mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrlib_dll.mxsrclib_dll

        self.measured_value = None

        self.p_double = (ctypes.c_double * 1)()

    def connect(self, a_measure_type: MeasureType, a_interface_name: str, a_gpib_index: int, a_gpib_address: int,
                a_com_name: str, a_ip: str, a_port: int) -> bool:

        # ВНИМАНИЕ! Макрос IRS_LIB_DEBUG в irsconfig.h для mxsrclib_dll должен быть отключен!!! Иначе крашнется

        result = self.mxsrclib_dll.connect_to_agilent_3458a(ctypes.c_size_t(a_measure_type),
            ctypes.c_wchar_p(a_interface_name), ctypes.c_int(a_gpib_index), ctypes.c_int(a_gpib_address),
            ctypes.c_wchar_p(a_com_name), ctypes.c_wchar_p(a_ip), ctypes.c_wchar_p(str(a_port)))

        if result:
            self.measured_value = a_measure_type

        return bool(result)

    def disconnect(self):
        self.measured_value = None
        self.mxsrclib_dll.disconnect_multimeter()

    def get_measured_value(self):
        assert self.measured_value is not None, "Мультиметр не инициализирован!"

        have_value = self.mxsrclib_dll.multimeter_get_measured_value(ctypes.c_size_t(self.measured_value), self.p_double)
        return have_value, self.p_double[0]


if __name__ == "__main__":
    a = Agilent3485A()
    a.connect(MeasureType.tm_volt_dc, "Agilent USB-GPIB", 0, 22, "", "", 123)
