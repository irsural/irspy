from enum import IntEnum
from typing import List
import logging
import struct
import re

import irspy.clb.calibrator_constants as clb
from irspy.clb.clb_dll import ClbDrv
import irspy.utils as utils


class VariableInfo:
    """
    Класс для описания сетевой переменной
    """
    def __init__(self, a_number: int = 0, a_index: int = 0, a_bit_index: int = 0, a_type: str = "u32",
                 a_name: str = ""):
        """
        :param a_number: Порядковый номер переменной
        :param a_index: Смещение переменной
        :param a_bit_index: Смещение бита переменной (Используется только когда a_type == "bit")
        :param a_type: Тип переменной
        :param a_name: Имя переменной
        """
        self.number = a_number
        self.index = a_index
        self.name = a_name
        self.size = 0
        self.c_type = ""
        self.bit_index = a_bit_index

        self.__type = a_type
        self.type = self.__type

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, a_type: str):
        self.__type = a_type
        self.c_type = VariableInfo.__get_c_type(self.__type)
        self.size = VariableInfo.__get_type_size(self.__type)

    @staticmethod
    def __get_type_size(a_type_name: str) -> int:
        """
        Возвращает размер типа в байтах по имени, для неучтенных типов бросает исключение TypeError
        :param a_type_name: Имя типа
        :return: Размер типа в байтах
        """
        if a_type_name == "double":
            return 8
        elif a_type_name == "float":
            return 4
        elif "32" in a_type_name:
            return 4
        elif "16" in a_type_name:
            return 2
        elif "8" in a_type_name:
            return 1
        elif a_type_name == "bit":
            return 1
        elif a_type_name == "bool":
            return 1
        elif "64" in a_type_name:
            return 8
        elif "long" in a_type_name:
            return 10
        else:
            raise TypeError(f"Незарегистрированый тип '{a_type_name}'")

    @staticmethod
    def __get_c_type(a_type_name: str) -> str:
        """
        Возвращает короткое имя типа по обычному имени, для неучтенных типов бросает исключение TypeError
        :param a_type_name: Имя типа
        :return: Короткое имя типа
        """
        if a_type_name == "double":
            return 'd'
        elif a_type_name == "float":
            return 'f'
        elif a_type_name == "bit":
            # Используется как флаг
            return 'o'
        elif a_type_name == "u32":
            return 'I'
        elif a_type_name == "i32":
            return 'i'
        elif a_type_name == "u8":
            return 'B'
        elif a_type_name == "i8":
            return 'b'
        elif a_type_name == "u16":
            return 'H'
        elif a_type_name == "i16":
            return 'h'
        elif a_type_name == "bool":
            return 'B'
        elif a_type_name == "u64":
            return 'Q'
        elif a_type_name == "i64":
            return 'q'
        else:
            raise TypeError("WARNING! Незарегистрированый тип '{a_type_name}'")

    def __repr__(self):
        return f"{self.number}, {self.index}, {self.bit_index}, {self.name}, {self.__type}"


class NetworkVariables:
    """
    Класс, который содержит сетевые переменные калибратора (не все) список переменных периодически обновляется
    Информация о переменных (Смещение, имя, тип и т.д.) читаются из tstlan-совместимого файла
    """
    VARIABLE_RE = re.compile(r"^(?P<parameter>Name|Type)_(?P<number>\d+)=(?P<value>.*)")

    def __init__(self, a_variables_ini_path: str, a_calibrator: ClbDrv, a_variables_read_delay=1):
        """
        :param a_variables_ini_path: Путь к файлу с описанием сетевых переменных
        :param a_calibrator: Драйвер калибратора
        :param a_variables_read_delay: Передается во все BufferedVariable и задает время, которое переменная будет
        читаться из внутреннего буфера, вместо чтения из калибратора
        """
        self.__calibrator = a_calibrator
        self.__variables_info = self.get_variables_from_ini(a_variables_ini_path)

        self.short_circuit_password = BufferedVariable(a_variable_info=VariableInfo(a_index=20, a_type="u32"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.core_t_calibration = BufferedVariable(a_variable_info=VariableInfo(a_index=36, a_type="double"),
                                                   a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                   a_buffer_delay_s=a_variables_read_delay)

        self.shutdown_execute_password = BufferedVariable(a_variable_info=VariableInfo(a_index=24, a_type="u32"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.signal_on = BufferedVariable(a_variable_info=VariableInfo(a_index=60, a_bit_index=0, a_type="bit"),
                                          a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                          a_buffer_delay_s=a_variables_read_delay)

        self.reference_amplitude = BufferedVariable(a_variable_info=VariableInfo(a_index=61, a_type="double"),
                                                    a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                    a_buffer_delay_s=a_variables_read_delay)

        self.current_enabled = BufferedVariable(a_variable_info=VariableInfo(a_index=69, a_bit_index=0, a_type="bit"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.dc_enabled = BufferedVariable(a_variable_info=VariableInfo(a_index=69, a_bit_index=1, a_type="bit"),
                                           a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                           a_buffer_delay_s=a_variables_read_delay)

        self.reverse = BufferedVariable(a_variable_info=VariableInfo(a_index=69, a_bit_index=2, a_type="bit"),
                                        a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                        a_buffer_delay_s=a_variables_read_delay)

        self.release_firmware = BufferedVariable(a_variable_info=VariableInfo(a_index=69, a_bit_index=5, a_type="bit"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.has_correction = BufferedVariable(a_variable_info=VariableInfo(a_index=69, a_bit_index=6, a_type="bit"),
                                               a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                               a_buffer_delay_s=a_variables_read_delay)

        self.pid_ac_voltage_k = BufferedVariable(a_variable_info=VariableInfo(a_index=71, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.pid_ac_voltage_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=79, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.pid_ac_voltage_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=87, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.iso_ac_voltage_k = BufferedVariable(a_variable_info=VariableInfo(a_index=95, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.iso_ac_voltage_t = BufferedVariable(a_variable_info=VariableInfo(a_index=103, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.acv_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=111, a_type="double"),
                                               a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                               a_buffer_delay_s=a_variables_read_delay)

        self.pid_ac_current_k = BufferedVariable(a_variable_info=VariableInfo(a_index=119, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.pid_ac_current_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=127, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.pid_ac_current_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=135, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.iso_ac_current_k = BufferedVariable(a_variable_info=VariableInfo(a_index=143, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.iso_ac_current_t = BufferedVariable(a_variable_info=VariableInfo(a_index=151, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.aci_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=159, a_type="double"),
                                               a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                               a_buffer_delay_s=a_variables_read_delay)

        self.aci_preset_voltage_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=167,
                                                                                           a_type="double"),
                                                              a_calibrator=self.__calibrator,
                                                              a_mode=BufferedVariable.Mode.RW,
                                                              a_buffer_delay_s=a_variables_read_delay)

        self.dead_band = BufferedVariable(a_variable_info=VariableInfo(a_index=183, a_type="double"),
                                          a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                          a_buffer_delay_s=a_variables_read_delay)

        self.f_correct_off = BufferedVariable(a_variable_info=VariableInfo(a_index=199, a_bit_index=0, a_type="bit"),
                                              a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                              a_buffer_delay_s=a_variables_read_delay)

        self.ui_correct_off = BufferedVariable(a_variable_info=VariableInfo(a_index=199, a_bit_index=1, a_type="bit"),
                                               a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                               a_buffer_delay_s=a_variables_read_delay)

        self.error_occurred = BufferedVariable(a_variable_info=VariableInfo(a_index=199, a_bit_index=3, a_type="bit"),
                                               a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                               a_buffer_delay_s=a_variables_read_delay)

        self.use_eeprom_instead_of_sd_for_correct = BufferedVariable(a_variable_info=VariableInfo(
            a_index=199, a_bit_index=6, a_type="bit"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.clear_error_occurred_status = BufferedVariable(a_variable_info=VariableInfo(
            a_index=199, a_bit_index=4, a_type="bit"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.error_code = BufferedVariable(a_variable_info=VariableInfo(a_index=200, a_type="i32"),
                                           a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                           a_buffer_delay_s=a_variables_read_delay)

        self.error_index = BufferedVariable(a_variable_info=VariableInfo(a_index=204, a_type="u32"),
                                            a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                            a_buffer_delay_s=a_variables_read_delay)

        self.error_count = BufferedVariable(a_variable_info=VariableInfo(a_index=208, a_type="u32"),
                                            a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                            a_buffer_delay_s=a_variables_read_delay)

        self.source_manual_mode_password = BufferedVariable(a_variable_info=VariableInfo(a_index=216, a_type="u32"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.RW,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.fast_adc_slow = BufferedVariable(a_variable_info=VariableInfo(a_index=229, a_type="double"),
                                              a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                              a_buffer_delay_s=a_variables_read_delay)

        self.frequency = BufferedVariable(a_variable_info=VariableInfo(a_index=293, a_type="double"),
                                          a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                          a_buffer_delay_s=a_variables_read_delay)

        self.aux_stabilizer_4v_dac_code_float = BufferedVariable(a_variable_info=VariableInfo(a_index=374,
                                                                                              a_type="float"),
                                                                 a_calibrator=self.__calibrator,
                                                                 a_mode=BufferedVariable.Mode.RW,
                                                                 a_buffer_delay_s=a_variables_read_delay)

        self.aux_stabilizer_45v_dac_code_float = BufferedVariable(a_variable_info=VariableInfo(a_index=378,
                                                                                               a_type="float"),
                                                                  a_calibrator=self.__calibrator,
                                                                  a_mode=BufferedVariable.Mode.RW,
                                                                  a_buffer_delay_s=a_variables_read_delay)

        self.aux_stabilizer_600v_dac_code_float = BufferedVariable(a_variable_info=VariableInfo(a_index=382,
                                                                                                a_type="float"),
                                                                   a_calibrator=self.__calibrator,
                                                                   a_mode=BufferedVariable.Mode.RW,
                                                                   a_buffer_delay_s=a_variables_read_delay)

        self.relay_200_600 = BufferedVariable(a_variable_info=VariableInfo(
            a_index=406, a_bit_index=0, a_type="bit"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.relay_aux_stabilizer_600v = BufferedVariable(a_variable_info=VariableInfo(
            a_index=406, a_bit_index=1, a_type="bit"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.relay_aux_stabilizer_4v = BufferedVariable(a_variable_info=VariableInfo(
            a_index=406, a_bit_index=4, a_type="bit"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.final_stabilizer_dac_dc_level = BufferedVariable(a_variable_info=VariableInfo(a_index=416,
                                                                                           a_type="double"),
                                                              a_calibrator=self.__calibrator,
                                                              a_mode=BufferedVariable.Mode.R,
                                                              a_buffer_delay_s=a_variables_read_delay)

        self.aux_stabilizer_adc_dc_600v_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=428,
                                                                                                a_type="double"),
                                                                   a_calibrator=self.__calibrator,
                                                                   a_mode=BufferedVariable.Mode.R,
                                                                   a_buffer_delay_s=a_variables_read_delay)

        self.aux_stabilizer_adc_dc_40v_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=448,
                                                                                               a_type="double"),
                                                                  a_calibrator=self.__calibrator,
                                                                  a_mode=BufferedVariable.Mode.R,
                                                                  a_buffer_delay_s=a_variables_read_delay)

        self.aux_stabilizer_adc_dc_4v_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=468,
                                                                                              a_type="double"),
                                                                 a_calibrator=self.__calibrator,
                                                                 a_mode=BufferedVariable.Mode.R,
                                                                 a_buffer_delay_s=a_variables_read_delay)

        self.inner_stabilizer_12v_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=512, a_type="double"),
                                                             a_calibrator=self.__calibrator,
                                                             a_mode=BufferedVariable.Mode.R,
                                                             a_buffer_delay_s=a_variables_read_delay)

        self.inner_stabilizer_9v_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=520, a_type="double"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.R,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.inner_stabilizer_5v_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=528, a_type="double"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.R,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.inner_stabilizer_2_5v_pos_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=536,
                                                                                               a_type="double"),
                                                                  a_calibrator=self.__calibrator,
                                                                  a_mode=BufferedVariable.Mode.R,
                                                                  a_buffer_delay_s=a_variables_read_delay)

        self.inner_stabilizer_2_5v_neg_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=544,
                                                                                               a_type="double"),
                                                                  a_calibrator=self.__calibrator,
                                                                  a_mode=BufferedVariable.Mode.R,
                                                                  a_buffer_delay_s=a_variables_read_delay)

        self.cooling_power_supply_voltage = BufferedVariable(a_variable_info=VariableInfo(a_index=552, a_type="double"),
                                                             a_calibrator=self.__calibrator,
                                                             a_mode=BufferedVariable.Mode.R,
                                                             a_buffer_delay_s=a_variables_read_delay)

        self.analog_board_temperature_max = BufferedVariable(a_variable_info=VariableInfo(a_index=560, a_type="double"),
                                                             a_calibrator=self.__calibrator,
                                                             a_mode=BufferedVariable.Mode.RW,
                                                             a_buffer_delay_s=a_variables_read_delay)

        self.main_board_temperature_max = BufferedVariable(a_variable_info=VariableInfo(a_index=576, a_type="double"),
                                                           a_calibrator=self.__calibrator,
                                                           a_mode=BufferedVariable.Mode.RW,
                                                           a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_temperature_setpoint = BufferedVariable(a_variable_info=VariableInfo(a_index=584,
                                                                                                 a_type="double"),
                                                                    a_calibrator=self.__calibrator,
                                                                    a_mode=BufferedVariable.Mode.RW,
                                                                    a_buffer_delay_s=a_variables_read_delay)

        self.main_board_temperature = BufferedVariable(a_variable_info=VariableInfo(a_index=592, a_type="double"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_pid_k = BufferedVariable(a_variable_info=VariableInfo(a_index=600, a_type="double"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_pid_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=608, a_type="double"),
                                                      a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                      a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_pid_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=616, a_type="double"),
                                                      a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                      a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_iso_k = BufferedVariable(a_variable_info=VariableInfo(a_index=624, a_type="double"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_iso_t = BufferedVariable(a_variable_info=VariableInfo(a_index=632, a_type="double"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=640, a_type="double"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_pid_out = BufferedVariable(a_variable_info=VariableInfo(a_index=648, a_type="double"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.main_board_fun_speed = BufferedVariable(a_variable_info=VariableInfo(a_index=656, a_type="i32"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_temperature_max = BufferedVariable(a_variable_info=VariableInfo(a_index=660,
                                                                                               a_type="double"),
                                                                  a_calibrator=self.__calibrator,
                                                                  a_mode=BufferedVariable.Mode.RW,
                                                                  a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_temperature_setpoint = BufferedVariable(a_variable_info=VariableInfo(a_index=668,
                                                                                                        a_type="double"),
                                                                           a_calibrator=self.__calibrator,
                                                                           a_mode=BufferedVariable.Mode.RW,
                                                                           a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_temperature = BufferedVariable(a_variable_info=VariableInfo(a_index=676,
                                                                                           a_type="double"),
                                                              a_calibrator=self.__calibrator,
                                                              a_mode=BufferedVariable.Mode.R,
                                                              a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_pid_k = BufferedVariable(a_variable_info=VariableInfo(a_index=684, a_type="double"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.RW,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_pid_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=692, a_type="double"),
                                                             a_calibrator=self.__calibrator,
                                                             a_mode=BufferedVariable.Mode.RW,
                                                             a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_pid_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=700, a_type="double"),
                                                             a_calibrator=self.__calibrator,
                                                             a_mode=BufferedVariable.Mode.RW,
                                                             a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_iso_k = BufferedVariable(a_variable_info=VariableInfo(a_index=708, a_type="double"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.RW,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_iso_t = BufferedVariable(a_variable_info=VariableInfo(a_index=716, a_type="double"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.RW,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=724,
                                                                                              a_type="double"),
                                                                 a_calibrator=self.__calibrator,
                                                                 a_mode=BufferedVariable.Mode.RW,
                                                                 a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_pid_out = BufferedVariable(a_variable_info=VariableInfo(a_index=732,
                                                                                           a_type="double"),
                                                              a_calibrator=self.__calibrator,
                                                              a_mode=BufferedVariable.Mode.R,
                                                              a_buffer_delay_s=a_variables_read_delay)

        self.transistor_dc_10a_fun_speed = BufferedVariable(a_variable_info=VariableInfo(a_index=740, a_type="i32"),
                                                            a_calibrator=self.__calibrator,
                                                            a_mode=BufferedVariable.Mode.R,
                                                            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_temperature_max = BufferedVariable(a_variable_info=VariableInfo(a_index=744, a_type="double"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_temperature_setpoint = BufferedVariable(a_variable_info=VariableInfo(a_index=752,
                                                                                            a_type="double"),
                                                               a_calibrator=self.__calibrator,
                                                               a_mode=BufferedVariable.Mode.RW,
                                                               a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_temperature = BufferedVariable(a_variable_info=VariableInfo(a_index=760, a_type="double"),
                                                      a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                      a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_pid_k = BufferedVariable(a_variable_info=VariableInfo(a_index=768, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_pid_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=776, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_pid_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=784, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_iso_k = BufferedVariable(a_variable_info=VariableInfo(a_index=792, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_iso_t = BufferedVariable(a_variable_info=VariableInfo(a_index=800, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=808, a_type="double"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_polarity_pin = BufferedVariable(a_variable_info=VariableInfo(a_index=832, a_bit_index=2,
                                                                                    a_type="bit"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_ready = BufferedVariable(a_variable_info=VariableInfo(a_index=832, a_bit_index=3, a_type="bit"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_invert_polarity = BufferedVariable(a_variable_info=VariableInfo(a_index=832, a_bit_index=4,
                                                                                       a_type="bit"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_pid_out = BufferedVariable(a_variable_info=VariableInfo(a_index=816, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.peltier_1_amplitude_code_float = BufferedVariable(a_variable_info=VariableInfo(a_index=824,
                                                                                            a_type="double"),
                                                               a_calibrator=self.__calibrator,
                                                               a_mode=BufferedVariable.Mode.R,
                                                               a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_temperature_max = BufferedVariable(a_variable_info=VariableInfo(a_index=833, a_type="double"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_temperature_setpoint = BufferedVariable(a_variable_info=VariableInfo(a_index=841,
                                                                                            a_type="double"),
                                                               a_calibrator=self.__calibrator,
                                                               a_mode=BufferedVariable.Mode.RW,
                                                               a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_temperature = BufferedVariable(a_variable_info=VariableInfo(a_index=849, a_type="double"),
                                                      a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                      a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_pid_k = BufferedVariable(a_variable_info=VariableInfo(a_index=857, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_pid_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=865, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_pid_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=873, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_iso_k = BufferedVariable(a_variable_info=VariableInfo(a_index=881, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_iso_t = BufferedVariable(a_variable_info=VariableInfo(a_index=889, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=897, a_type="double"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_polarity_pin = BufferedVariable(a_variable_info=VariableInfo(a_index=921, a_bit_index=2,
                                                                                    a_type="bit"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_ready = BufferedVariable(a_variable_info=VariableInfo(a_index=921, a_bit_index=3, a_type="bit"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_invert_polarity = BufferedVariable(a_variable_info=VariableInfo(a_index=921, a_bit_index=4,
                                                                                       a_type="bit"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.peltier_2_pid_out = BufferedVariable(a_variable_info=VariableInfo(a_index=905, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_temperature_max = BufferedVariable(a_variable_info=VariableInfo(a_index=922, a_type="double"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_temperature_setpoint = BufferedVariable(a_variable_info=VariableInfo(a_index=930,
                                                                                            a_type="double"),
                                                               a_calibrator=self.__calibrator,
                                                               a_mode=BufferedVariable.Mode.RW,
                                                               a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_temperature = BufferedVariable(a_variable_info=VariableInfo(a_index=938, a_type="double"),
                                                      a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                      a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_pid_k = BufferedVariable(a_variable_info=VariableInfo(a_index=946, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_pid_ki = BufferedVariable(a_variable_info=VariableInfo(a_index=954, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_pid_kd = BufferedVariable(a_variable_info=VariableInfo(a_index=962, a_type="double"),
                                                 a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                 a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_iso_k = BufferedVariable(a_variable_info=VariableInfo(a_index=970, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_iso_t = BufferedVariable(a_variable_info=VariableInfo(a_index=978, a_type="double"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_rate_slope = BufferedVariable(a_variable_info=VariableInfo(a_index=986, a_type="double"),
                                                     a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                     a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_pid_out = BufferedVariable(a_variable_info=VariableInfo(a_index=994, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_polarity_pin = BufferedVariable(a_variable_info=VariableInfo(a_index=1010, a_bit_index=2,
                                                                                    a_type="bit"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_ready = BufferedVariable(a_variable_info=VariableInfo(a_index=1010, a_bit_index=3, a_type="bit"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_3_invert_polarity = BufferedVariable(a_variable_info=VariableInfo(a_index=1010, a_bit_index=4,
                                                                                       a_type="bit"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_temperature_max = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1011, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_temperature = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1019, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
            a_buffer_delay_s=a_variables_read_delay)

        self.volume = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1036, a_type="float"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.result_id = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1040, a_type="u32"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.f_calibr_coeff = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1064, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.time_calibr_coeff = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1088, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.id = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1098, a_type="u32"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.software_revision = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1108, a_type="u32"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_temperature_setpoint = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1130, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_pid_k = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1138, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_pid_ki = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1146, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_pid_kd = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1154, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_iso_k = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1162, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_iso_t = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1170, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_rate_slope = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1178, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_pid_out = BufferedVariable(a_variable_info=VariableInfo(a_index=1186, a_type="double"),
                                                  a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                  a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_polarity_pin = BufferedVariable(a_variable_info=VariableInfo(a_index=1202, a_bit_index=2,
                                                                                    a_type="bit"),
                                                       a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.R,
                                                       a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_ready = BufferedVariable(a_variable_info=VariableInfo(a_index=1202, a_bit_index=3, a_type="bit"),
                                                a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
                                                a_buffer_delay_s=a_variables_read_delay)

        self.peltier_4_invert_polarity = BufferedVariable(a_variable_info=VariableInfo(a_index=1202, a_bit_index=4,
                                                                                       a_type="bit"),
                                                          a_calibrator=self.__calibrator,
                                                          a_mode=BufferedVariable.Mode.RW,
                                                          a_buffer_delay_s=a_variables_read_delay)

        self.fun_max_level_for_low_dcv = BufferedVariable(a_variable_info=VariableInfo(
            a_index=1237, a_type="double"), a_calibrator=self.__calibrator, a_mode=BufferedVariable.Mode.RW,
            a_buffer_delay_s=a_variables_read_delay)

    @staticmethod
    def get_variables_from_ini(a_ini_path: str) -> List[VariableInfo]:
        """
        Парсит ini-файл с информацией о сетевых переменных и возвращает список VariableInfo
        :param a_ini_path: Путь к ini-файлу
        :return: Список VariableInfo, содержащий информацию о сетевых переменных
        """
        variables_info = []
        with open(a_ini_path) as config:
            for line in config:
                variable_re = NetworkVariables.VARIABLE_RE.match(line)
                if variable_re is not None:
                    number = int(variable_re.group('number'))
                    value = variable_re.group('value')

                    if number >= len(variables_info):
                        assert (number - len(variables_info)) < 1, f"Переменные в конфиге расположены не по порядку"
                        variables_info.append(VariableInfo(a_number=number))

                    if variable_re.group('parameter') == "Name":
                        variables_info[number].name = value
                    else:
                        variables_info[number].type = value

                        if number != 0:
                            current_var = variables_info[number]
                            prev_var = variables_info[number - 1]

                            if current_var.type == "bit":
                                if prev_var.type == "bit":
                                    if prev_var.bit_index == 7:
                                        current_var.index = prev_var.index + 1
                                        current_var.bit_index = 0
                                    else:
                                        current_var.index = prev_var.index
                                        current_var.bit_index = prev_var.bit_index + 1
                                else:
                                    current_var.index = prev_var.index + prev_var.size
                            else:
                                current_var.index = prev_var.index + prev_var.size
        return variables_info

    def get_variables_info(self) -> List[VariableInfo]:
        """
        Возвращает список VariableInfo с информацией о сетевых переменных
        """
        return self.__variables_info

    def get_data_size(self) -> int:
        """
        Возвращает размер памяти, который занимают сетевые переменные
        """
        return self.__variables_info[-1].index + self.__variables_info[-1].size

    def connected(self) -> bool:
        """
        Возвращает True, если соединение с калибратором установлено, иначе False
        """
        return self.__calibrator.state != clb.State.DISCONNECTED

    def read_variable(self, a_variable_number: int):
        """
        Читает значение сетевой переменной по номеру
        :param a_variable_number: Номер сетевой переменной
        :return: Значение сетевой переменной
        """
        variable_info = self.__variables_info[a_variable_number]
        if variable_info.c_type == 'o':
            return self.__calibrator.read_bit(variable_info.index, variable_info.bit_index)
        else:
            _bytes = self.__calibrator.read_raw_bytes(variable_info.index, variable_info.size)
            return struct.unpack(variable_info.c_type, _bytes)[0]

    def write_variable(self, a_variable_number: int, a_variable_value):
        """
        Записывает значение в сетевую переменную по ее номеру
        :param a_variable_number: Номер сетевой переменной
        :param a_variable_value: Значение, которое необходимо записать
        """
        variable_info = self.__variables_info[a_variable_number]
        if variable_info.c_type == 'o':
            value = int(utils.bound(a_variable_value, 0, 1))
            self.__calibrator.write_bit(variable_info.index, variable_info.bit_index, value)
        else:
            if variable_info.c_type != 'd' and variable_info.c_type != 'f':
                a_variable_value = int(a_variable_value)

            _bytes = struct.pack(variable_info.c_type, a_variable_value)
            self.__calibrator.write_raw_bytes(variable_info.index, variable_info.size, _bytes)


class BufferedVariable:
    """
    Класс для буферизации значений сетевых переменных. Нужен, когда необходимо, чтобы чтение сетевой переменной
    сразу после ее записи возвращала только что записанное значение.
    (Если читать просто сетевую переменную, то чтение вернет старое значение, т.к. mxdata обновляется не мгновенно)
    """
    class Mode(IntEnum):
        R = 0
        RW = 1

    def __init__(self, a_variable_info: VariableInfo, a_calibrator: ClbDrv, a_mode: Mode = Mode.RW,
                 a_buffer_delay_s: float = 1):
        """
        :param a_variable_info: Информация о сетевой переменной
        :param a_calibrator: Драйвер калибратора
        :param a_mode: Режим доступа (R / RW). Если переменная в режиме R, то запись в нее бросает PermissionError
        :param a_buffer_delay_s: Время в секундах, в течение которого значение переменной должно читаться из буфера
        """
        assert a_variable_info.c_type != "", "variable must have a c_type"
        assert a_variable_info.type != "", "variable must have a type"
        assert a_variable_info.size != 0, "variable must have a non-zero size"

        self.__variable_info = a_variable_info
        self.__is_bit = True if a_variable_info.c_type == 'o' else False
        self.__mode = a_mode
        self.__calibrator = a_calibrator

        self.__buffer = 0
        self._buffer_delay = a_buffer_delay_s
        self.__delay_timer = utils.Timer(self._buffer_delay)

    def get(self):
        if self.__delay_timer.check() or not self.__delay_timer.started():
            if self.__is_bit:
                return self.__calibrator.read_bit(self.__variable_info.index, self.__variable_info.bit_index)
            else:
                _bytes = self.__calibrator.read_raw_bytes(self.__variable_info.index, self.__variable_info.size)
                return struct.unpack(self.__variable_info.c_type, _bytes)[0]
        else:
            return self.__buffer

    def set(self, a_value):
        if self.__mode == BufferedVariable.Mode.R:
            raise PermissionError(f"Попытка записи в read-only переменную "
                                  f"(Индекс: {self.__variable_info.index}.{self.__variable_info.bit_index})")

        if self.__is_bit:
            a_value = utils.bound(int(a_value), 0, 1)
            self.__calibrator.write_bit(self.__variable_info.index, self.__variable_info.bit_index, a_value)
        else:
            if self.__variable_info.c_type != 'd' and self.__variable_info.c_type != 'f':
                a_value = int(a_value)

            _bytes = struct.pack(self.__variable_info.c_type, a_value)
            self.__calibrator.write_raw_bytes(self.__variable_info.index, self.__variable_info.size, _bytes)

        self.__buffer = a_value
        self.__delay_timer.start()
