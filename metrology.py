from collections import deque


class StabilityControl:
    pass


class MovingAverage:
    def __init__(self, a_window_size: int = 0):
        self.__window_size = a_window_size
        self.__sum = 0

        if self.__window_size:
            self.__values = deque(maxlen=a_window_size)
        else:
            self.__values = deque()

    def reset(self, a_window_size=None):
        if a_window_size:
            self.__window_size = a_window_size
        self.__sum = 0

        if self.__window_size:
            self.__values = deque(maxlen=a_window_size)
        else:
            self.__values = deque()

    def add(self, a_value: float):
        if self.__window_size > 0 and len(self.__values) == self.__window_size:
            popped_value = self.__values[0]
            self.__sum -= popped_value
        self.__sum += a_value

        self.__values.append(a_value)

    def is_empty(self):
        return not self.__values

    def get(self):
        if self.__values:
            return self.__sum / len(self.__values)
        else:
            return 0

