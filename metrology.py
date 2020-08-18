from collections import deque
from array import array
from math import sqrt
import logging
import ctypes

from irspy.dlls import mxsrlib_dll


def deviation_percents(a_value: float, a_reference: float):
    assert a_reference != 0, "a_reference must not be zero"
    return (a_value - a_reference) / abs(a_reference) * 100


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


class MovingSKO:
    def __init__(self, a_window_size: int = 0):
        self.__window_size = a_window_size
        self.__average = MovingAverage(self.__window_size)
        self.__squares_sum = 0

        if self.__window_size:
            self.__squares = deque(maxlen=a_window_size)
        else:
            self.__squares = deque()

    def reset(self, a_window_size=None):
        if a_window_size:
            self.__window_size = a_window_size

        self.__average.reset()
        self.__squares_sum = 0

        if self.__window_size:
            self.__squares = deque(maxlen=a_window_size)
        else:
            self.__squares = deque()

    def add(self, a_value: float):
        self.__average.add(a_value)

        if self.__window_size > 0 and len(self.__squares) == self.__window_size:
            popped_value = self.__squares[0]
            self.__squares_sum -= popped_value

        square = (a_value - self.__average.get()) ** 2
        self.__squares_sum += square
        self.__squares.append(square)

    def is_empty(self):
        return not self.__squares

    def average(self):
        return self.__average.get()

    def get(self):
        if self.__squares and self.__squares_sum >= 0:

            return sqrt(self.__squares_sum / len(self.__squares))
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


class ParamFilter:
    def __init__(self):
        assert mxsrlib_dll.mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrlib_dll.mxsrclib_dll

    def tick(self):
        self.mxsrclib_dll.param_filter_tick()

    def add(self, a_value: float):
        self.mxsrclib_dll.param_filter_add(a_value)

    def get_value(self) -> float:
        return self.mxsrclib_dll.param_filter_get_value()

    def restart(self):
        self.mxsrclib_dll.param_filter_restart()

    def set_sampling_time(self, a_sampling_time: float):
        self.mxsrclib_dll.param_filter_set_sampling_time(a_sampling_time)

    def resize(self, a_new_size: int):
        self.mxsrclib_dll.param_filter_resize(a_new_size)

    def stop(self):
        self.mxsrclib_dll.param_filter_stop()


if __name__ == "__main__":
    from irspy.dlls import mxsrlib_dll
    from array import array

    mxsrclib_dll = mxsrlib_dll.set_up_mxsrclib_dll("dlls/mxsrclib_dll.dll")

    param_filter = ParamFilter()
    param_filter.stop()
    param_filter.resize(100)
    param_filter.set_sampling_time(0.1)

    param_filter.restart()

    for i in range(110000):
        print(i / 110000000 * 100)
        param_filter.add(i / 100)
        param_filter.tick()

    param_filter.stop()
    print(param_filter.get_value())
