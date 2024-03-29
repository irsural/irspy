from typing import Dict, Tuple
import enum

from irspy.utils import bound
from irspy.utils import parse_input


MAX_CURRENT = 11
MIN_CURRENT = -11

MAX_VOLTAGE = 630
MIN_VOLTAGE = -630

MIN_AC_AMPLITUDE = 0

MAX_FREQUENCY = 2000
MIN_FREQUENCY = 40

SHORT_CIRCUIT_PASSWORD = 4242
MANUAL_MODE_ENABLE_PASSWORD = 8925
SHUTDOWN_EXECUTE_PASSWORD = 5298

CLB_CONFIG_NAME = "Calibrator 2.ini"


class Polarity(enum.IntEnum):
    POS = 0
    NEG = 1


polarity_to_text = {
    Polarity.POS: "+",
    Polarity.NEG: "-"
}


class SignalType(enum.IntEnum):
    ACI = 0
    ACV = 1
    DCI = 2
    DCV = 3


class Mode(enum.IntEnum):
    SOURCE = 0
    FIXED_RANGE = 1
    DETUNING = 2


class State(enum.IntEnum):
    DISCONNECTED = 0
    STOPPED = 1
    WAITING_SIGNAL = 2
    READY = 3


state_to_text = {
    State.DISCONNECTED: "Соединение отсутствует",
    State.STOPPED: "Остановлен",
    State.WAITING_SIGNAL: "Установка сигнала...",
    State.READY: "Готов"
}

mode_to_text = {
    Mode.SOURCE: "Источник",
    Mode.FIXED_RANGE: "Фиксированный",
    Mode.DETUNING: "Расстройка",
}

signal_type_to_text = {
    SignalType.ACI: "Переменный ток",
    SignalType.ACV: "Переменное напряжение",
    SignalType.DCI: "Постоянный ток",
    SignalType.DCV: "Постоянное напряжение"
}

signal_type_to_text_short = {
    SignalType.ACI: "I~",
    SignalType.ACV: "U~",
    SignalType.DCI: "I=",
    SignalType.DCV: "U="
}

signal_type_to_units = {
    SignalType.ACI: "А",
    SignalType.DCI: "А",
    SignalType.ACV: "В",
    SignalType.DCV: "В"
}

is_dc_signal = {
    SignalType.ACI: False,
    SignalType.ACV: False,
    SignalType.DCI: True,
    SignalType.DCV: True
}

is_ac_signal = {
    SignalType.ACI: True,
    SignalType.ACV: True,
    SignalType.DCI: False,
    SignalType.DCV: False
}

is_voltage_signal = {
    SignalType.ACI: False,
    SignalType.DCI: False,
    SignalType.ACV: True,
    SignalType.DCV: True
}

is_amperes_signal = {
    SignalType.ACI: True,
    SignalType.DCI: True,
    SignalType.ACV: False,
    SignalType.DCV: False
}

signal_type_to_min_step = {
    SignalType.ACI: 2e-6,
    SignalType.ACV: 2e-6,
    SignalType.DCI: 2e-9,
    SignalType.DCV: 2e-7,
}

signal_type_to_current_enabled_bit = {
    SignalType.ACI: True,
    SignalType.DCI: True,
    SignalType.ACV: False,
    SignalType.DCV: False
}

signal_type_to_dc_enabled_bit = {
    SignalType.ACI: False,
    SignalType.DCI: True,
    SignalType.ACV: False,
    SignalType.DCV: True
}


error_code_to_message = {
    257: "Перегрев аналоговой платы",
    258: "Перегрев платы питания",
    259: "Перегрев транзистора постоянного тока 10 А",
    260: "Перегрев элемента Пельтье №1",
    261: "Перегрев элемента Пельтье №2",
    262: "Перегрев элемента Пельтье №3",
    263: "Перегрев элемента Пельтье №4",
    4104: "Нестабильное напряжение на стабилизаторе 12 В",
    4105: "Нестабильное напряжение на стабилизаторе 9 В",
    4106: "Нестабильное напряжение на стабилизаторе 5 В",
    4107: "Нестабильное напряжение на стабилизаторе +2,5 В",
    4108: "Нестабильное напряжение на стабилизаторе -2,5 В",
    4109: "Нестабильное напряжение на источнике питания вентиляторов",
    4110: "Стабилизатор 4 В не вышел на режим",
    4111: "Стабилизатор 45 В не вышел на режим",
    4112: "Стабилизатор 650 В не вышел на режим",
    4113: "Не удалось выйти на режим",
    4114: "Не удалось выйти на режим, слишком большое сопротивление",
    4115: "Превышение тока",
    4116: "Не удалось выделить память",
    4117: "Сторожевой таймер перезагрузил установку",
    4118: "Ошибка при чтении основных настроек",
    4119: "Слишком много ошибок",
    4120: "Сброс EEPROM Пельтье 4",
    4121: "Слишком низкое сопротивление нагрузки. Прибор не может выйти на режим",
    4122: "Обнаружено короткое замыкание",
    129: "SD карта не обнаружена. Калибровка прибора нарушена",
    140: "Не удалось смонтировать файловую систему. Калибровка прибора нарушена",
}


class DcvRanges(enum.Enum):
    DCV_40mv = "40 мВ"
    DCV_420mv = "420 мВ"
    DCV_4_08v = "4.08 В"
    DCV_42_9v = "42.9 В"
    DCV_200v = "200 В"
    DCV_635v = "635 В"


class DciRanges(enum.Enum):
    DCI_110mca = "110 мкА"
    DCI_1_11mA = "1.1 мА"
    DCI_11ma = "11 мА"
    DCI_110ma = "110 мА"
    DCI_1_1a = "1.1 А"
    DCI_10a = "11 А"


class AcvRanges(enum.Enum):
    ACV_110mv = "110 мВ"
    ACV_1_1v = "1.1 В"
    ACV_11v = "11 В"
    ACV_110v = "110 В"
    ACV_630v = "630 В"


class AciRanges(enum.Enum):
    ACI_110ma = "110 мА"
    ACI_1_1a = "1.1 А"
    ACI_11a = "11 А"


class SignalRange(enum.Enum):
    DCV = DcvRanges
    DCI = DciRanges
    ACV = AcvRanges
    ACI = AciRanges


def __make_range_limits() -> Dict[SignalRange, Tuple[float, float]]:
    range_limits = {}
    lower_limit = 0
    for signal in SignalRange:
        for range in signal.value:
            upper_limit = parse_input(range.value)

            if upper_limit < lower_limit:
                # Следующий тип сигнала
                lower_limit = 0

            range_limits[range] = (lower_limit, upper_limit)
            lower_limit = upper_limit

    return range_limits


RANGE_LIMITS = __make_range_limits()

SIGNAL_TYPE_RANGES = {
    SignalType.DCV: DcvRanges,
    SignalType.DCI: DciRanges,
    SignalType.ACV: AcvRanges,
    SignalType.ACI: AciRanges
}


def bound_amplitude(a_amplitude: float, a_signal_type: SignalType) -> float:
    """
    Обрезает амплитуду в допустимых для калибратора границах, в зависимости от типа сигнала
    Для постоянных типов сигнала может возвращать амплитуду с отрицательным знаком
    :param a_amplitude: Уставка амплитуды
    :param a_signal_type: Тип сигнала
    :return: Обрезанная уставка амплитуды
    """
    min_value = MIN_VOLTAGE
    max_value = MAX_VOLTAGE
    if not is_voltage_signal[a_signal_type]:
        min_value = MIN_CURRENT
        max_value = MAX_CURRENT
    if is_ac_signal[a_signal_type]:
        min_value = MIN_AC_AMPLITUDE
    return round(bound(a_amplitude, min_value, max_value), 9)


def bound_frequency(a_frequency: float, a_signal_type: SignalType) -> float:
    """
    Обрезает частоту в допустимых для калибратора границах, в зависимости от типа сигнала (постоянный или переменный)
    Если тип сигнала постоянный, то всегда возвращает 0
    :param a_frequency: Уставка частоты
    :param a_signal_type: Тип сигнала
    :return: Обрезанная уставка частоты
    """
    min_frequency = MIN_FREQUENCY if is_ac_signal[a_signal_type] else 0
    max_frequency = MAX_FREQUENCY if is_ac_signal[a_signal_type] else 0
    return round(bound(a_frequency, min_frequency, max_frequency), 9)
