from clb.network_variables import BufferedVariable
from utils import Timer


class FlagStabilityChecker:
    """
    Проверяет, что переменная калибратора находится в заданном состоянии заданное время
    """
    def __init__(self, a_flag_variable: BufferedVariable, a_hold_flag_time, a_check_state=True):
        self.flag_variable = a_flag_variable
        self.hold_flag_timer = Timer(a_hold_flag_time)
        self.check_state = a_check_state

    def start(self):
        self.hold_flag_timer.start()

    def check(self) -> bool:
        if self.flag_variable.get() != self.check_state:
            self.start()
        return self.hold_flag_timer.check()


def guaranteed_buffered_variable_set(a_buffered_variable: BufferedVariable, value):
    """
    Проверяет, соответствует ли значение a_buffered_variable значению value.
    Если не соответствует, то устанавливает a_buffered_variable = value
    !! ВНИМАНИЕ !! Параметр a_buffer_delay_s у a_buffered_variable должен быть равен нулю !!!
    :return: True, если значние a_buffered_variable = value, иначе False
    """
    if a_buffered_variable.get() == value:
        return True
    else:
        a_buffered_variable.set(value)
        return False
