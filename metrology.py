from collections import deque


class MovingAverage:
    def __init__(self, a_window_size: int):
        assert a_window_size != 0, "Размер окна не может быть равен нулю"

        self.__window_size = a_window_size
        self.__values = deque(maxlen=a_window_size)
        self.__sum = 0

    def reset(self, a_window_size=None):
        if a_window_size:
            self.__window_size = a_window_size

        self.__values = deque(maxlen=self.__window_size)
        self.__sum = 0

    def add(self, a_value: float):
        if len(self.__values) == self.__window_size:
            popped_value = self.__values[0]
            self.__sum -= popped_value
        self.__sum += a_value

        self.__values.append(a_value)

    def get(self):
        if self.__values:
            return self.__sum / len(self.__values)
        else:
            return 0

