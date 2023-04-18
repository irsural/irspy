from irspy.clb.network_variables import BufferedVariable, NetworkVariables
import irspy.clb.calibrator_constants as clb


def guaranteed_buffered_variable_set(a_buffered_variable: BufferedVariable, value) -> bool:
    """
    Проверяет, соответствует ли значение a_buffered_variable значению value.
    Если не соответствует, то устанавливает a_buffered_variable = value
    !! ВНИМАНИЕ !! Параметр a_buffer_delay_s у a_buffered_variable должен быть равен нулю !!!
    :return: True, если значние a_buffered_variable = value, иначе False
    """
    assert a_buffered_variable._buffer_delay == 0, "Задержка чтения должна быть равна нулю!"

    if a_buffered_variable.get() == value:
        return True
    else:
        a_buffered_variable.set(value)
        return False


def guaranteed_set_signal_type(a_network_variables: NetworkVariables, a_signal_type: clb.SignalType) -> bool:
    current_enabled = clb.signal_type_to_current_enabled_bit[a_signal_type]
    dc_enabled = clb.signal_type_to_dc_enabled_bit[a_signal_type]

    current_ok = guaranteed_buffered_variable_set(a_network_variables.current_enabled, current_enabled)
    dc_ok = guaranteed_buffered_variable_set(a_network_variables.dc_enabled, dc_enabled)

    return current_ok and dc_ok
