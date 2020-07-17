from collections import deque
from array import array
import ctypes

from irspy.dlls import mxsrlib_dll


def deviation_percents(a_value: float, a_reference: float):
    assert a_reference != 0, "a_reference must not be zero"
    return (a_reference - a_value) / abs(a_reference) * 100


def student_t_inverse_distribution_2x(a_confidence_level, a_degrees_of_freedom):
    assert mxsrlib_dll.mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
    assert a_degrees_of_freedom > 0, "Количество степеней свободы должно быть больше 0"
    assert a_confidence_level in (0.95, 0.99, 0.999), "Допустимые уровни доверия: 0.95, 0.99, 0.999"

    return mxsrlib_dll.mxsrclib_dll.student_t_inverse_distribution_2x(a_confidence_level, a_degrees_of_freedom)


class StabilityControl:
    pass


class MovingAverage:
    def __init__(self, a_window_size: int = 0):
        self.__window_size = a_window_size
        self.__sum = 0

        if self.__window_size:
            self.__samples = deque(maxlen=a_window_size)
        else:
            self.__samples = deque()

    def reset(self, a_window_size=None):
        if a_window_size:
            self.__window_size = a_window_size
        self.__sum = 0

        if self.__window_size:
            self.__samples = deque(maxlen=a_window_size)
        else:
            self.__samples = deque()

    def add(self, a_value: float):
        if self.__window_size > 0 and len(self.__samples) == self.__window_size:
            popped_value = self.__samples[0]
            self.__sum -= popped_value
        self.__sum += a_value

        self.__samples.append(a_value)

    def is_empty(self):
        return not self.__samples

    def get(self):
        if self.__samples:
            return self.__sum / len(self.__samples)
        else:
            return 0


class ImpulseFilter:
    MIN_SIZE = 3

    def __init__(self):
        assert mxsrlib_dll.mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrlib_dll.mxsrclib_dll

    def clear(self):
        self.mxsrclib_dll.imp_filter_clear()

    def add(self, a_value: float):
        self.mxsrclib_dll.imp_filter_add(a_value)

    def get(self) -> float:
        return self.mxsrclib_dll.imp_filter_get()

    def assign(self, a_values: array):
        address, size = a_values.buffer_info()
        assert size >= 3, "Для корректной работы в импульсный фильтр нужно задать как минимум 3 значения!"

        pointer_to_double = ctypes.cast(address, ctypes.POINTER(ctypes.c_double))
        self.mxsrclib_dll.imp_filter_assign(pointer_to_double, size)


if __name__ == "__main__":
    import os
    from irspy.dlls import mxsrlib_dll
    from array import array

    mxsrclib_dll = mxsrlib_dll.set_up_mxsrclib_dll("dlls/mxsrclib_dll.dll")

    impulse_filter = ImpulseFilter()
    impulse_filter.clear()

    directory = "D:\\proj\\autocalibration\\autocalibration\\configurations"
    for file in os.listdir(directory):
        if file.startswith("test_data"):
            with open(f"{directory}\\{file}", "r") as data_file:

                expect_result = float(data_file.readline())
                print("expected:", expect_result)

                data_to_filter = array('d')
                impulse_filter.clear()

                for line in data_file:
                    value = float(line)
                    data_to_filter.append(value)

                impulse_filter.assign(data_to_filter)

                print("got:", impulse_filter.get())
                print("diff percents:", (expect_result - impulse_filter.get()) / expect_result * 100)
                print()
