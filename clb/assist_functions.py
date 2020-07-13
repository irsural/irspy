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
