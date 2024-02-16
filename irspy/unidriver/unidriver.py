import ctypes
from enum import IntEnum

from irspy.unidriver.types import Device


class UnidriverDLLWrapper:
    def __init__(self, unidriver_dll_path: str) -> None:
        self.__dll = self.__setup_dll(unidriver_dll_path)

    @property
    def dll(self) -> ctypes.CDLL:
        return self.__dll

    @staticmethod
    def __setup_dll(dll_path: str) -> ctypes.CDLL:
        dll = ctypes.CDLL(dll_path)
        handle_t = ctypes.c_int32
        res_t = ctypes.c_int32
        param_t = ctypes.c_size_t
        enum_t = ctypes.c_int32
        counter_t = ctypes.c_int64

        dll.get_groups_info.restype = res_t
        dll.get_groups_info.argtypes = [ctypes.c_char_p, ctypes.c_size_t]

        dll.get_device_info.restype = res_t
        dll.get_device_info.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
                                        ctypes.c_size_t]

        dll.builder_create.restype = res_t
        dll.builder_create.argtypes = [ctypes.c_size_t, ctypes.c_size_t]

        dll.builder_apply.restype = res_t
        dll.builder_apply.argtypes = [handle_t]

        dll.builder_set_param_double.restype = res_t
        dll.builder_set_param_double.argtypes = [handle_t, param_t, ctypes.c_double]

        dll.builder_set_param_int32.restype = res_t
        dll.builder_set_param_int32.argtypes = [handle_t, param_t, ctypes.c_int32]

        dll.builder_set_param_u8str.restype = res_t
        dll.builder_set_param_u8str.argtypes = [handle_t, param_t, ctypes.c_char_p,
                                                ctypes.c_size_t]

        dll.builder_set_param_enum.restype = res_t
        dll.builder_set_param_enum.argtypes = [handle_t, param_t, ctypes.c_int32]

        dll.builder_set_param_counter.restype = res_t
        dll.builder_set_param_counter.argtypes = [handle_t, param_t, ctypes.c_int64]

        dll.tick_all.restype = res_t

        dll.read_bytes.restype = res_t
        dll.read_bytes.argtypes = [handle_t, ctypes.c_char_p, ctypes.c_size_t,
                                   ctypes.c_size_t]

        dll.write_bytes.restype = res_t
        dll.write_bytes.argtypes = [handle_t, ctypes.c_char_p, ctypes.c_size_t,
                                    ctypes.c_size_t]

        dll.read_bit.restype = res_t
        dll.read_bit.argtypes = [handle_t, ctypes.c_size_t, ctypes.c_size_t]

        dll.write_bit.restype = res_t
        dll.write_bit.argtypes = [handle_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_bool]

        dll.data_size.restype = res_t
        dll.data_size.argtypes = [handle_t]

        dll.is_connected.restype = res_t
        dll.is_connected.argtypes = [handle_t]

        dll.release.restype = res_t
        dll.release.argtypes = [handle_t]

        dll.get_error_descriptions.restype = res_t
        dll.get_error_descriptions.argtypes = [ctypes.c_char_p, ctypes.c_size_t]

        dll.get_error_description.restype = res_t
        dll.get_error_description.argtypes = [ctypes.c_int32, ctypes.c_char_p,
                                              ctypes.c_size_t]

        dll.create_udp_client_flow.restype = res_t
        dll.create_udp_client_flow.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

        dll.create_tcp_client_flow.restype = res_t
        dll.create_tcp_client_flow.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        dll.create_udp_server_flow.restype = res_t
        dll.create_udp_server_flow.argtypes = [ctypes.c_char_p]
        dll.create_tcp_server_flow.restype = res_t
        dll.create_tcp_server_flow.argtypes = [ctypes.c_char_p]
        # Only windows
        dll.create_ni_usb_gpib_flow.restype = res_t
        dll.create_ni_usb_gpib_flow.argtypes = [ctypes.c_size_t, ctypes.c_size_t, ctypes.c_double,
                                                ctypes.c_double, ctypes.c_char_p]

        dll.create_prologix_flow.restype = res_t
        dll.create_prologix_flow.argtypes = [handle_t, ctypes.c_size_t, enum_t, enum_t,
                                             ctypes.c_size_t]

        dll.create_multimeter_mxdata.restype = res_t
        dll.create_multimeter_mxdata.argtypes = [handle_t, ctypes.c_double]
        dll.create_akip_v7_78_1_mult.restype = res_t
        dll.create_akip_v7_78_1_mult.argtypes = [handle_t, enum_t]
        dll.create_modbus_client.restype = res_t
        dll.create_modbus_client.argtypes = [handle_t, enum_t, ctypes.c_size_t, ctypes.c_size_t,
                                             ctypes.c_size_t, ctypes.c_size_t, counter_t]
        dll.create_modbus_server.restype = res_t
        dll.create_modbus_server.argtypes = [handle_t, ctypes.c_size_t, ctypes.c_size_t,
                                             ctypes.c_size_t, ctypes.c_size_t, counter_t]
        dll.create_mxnet_client.restype = res_t
        dll.create_mxnet_client.argtypes = [handle_t, counter_t, counter_t]
        dll.create_mxnet_server.restype = res_t
        dll.create_mxnet_server.argtypes = [handle_t, ctypes.c_size_t]

        return dll


class UnidriverIO:
    def __init__(self, dll_wrapper: UnidriverDLLWrapper) -> None:
        self.__dll = dll_wrapper.dll

    def read_bytes(self, handle: int, index: int, size: int) -> bytes:
        assert handle >= 0
        assert index >= 0
        assert size > 0
        buf = ctypes.create_string_buffer(size)
        ret = self.__dll.read_bytes(handle, buf, index, size)
        assert ret == 0, f'Error, code: {ret}'
        return buf.raw

    def write_bytes(self, handle: int, index: int, value: bytes) -> None:
        assert handle >= 0
        assert index >= 0
        assert len(value) > 0
        buf = ctypes.create_string_buffer(value)
        ret = self.__dll.write_bytes(handle, buf, index, len(value))
        assert ret == 0, f'Error, code: {ret}'

    def read_bit(self, handle: int, byte_index: int, bit_index: int) -> bool:
        assert handle >= 0
        assert byte_index >= 0
        assert 0 <= bit_index < 8
        ret = self.__dll.read_bit(handle, byte_index, bit_index)
        assert ret >= 0, f'Error, code: {ret}'
        return bool(ret)

    def write_bit(self, handle: int, byte_index: int, bit_index: int, value: bool) -> None:
        assert handle >= 0
        assert byte_index >= 0
        assert 0 <= bit_index < 8
        ret = self.__dll.write_bit(handle, byte_index, bit_index, value)
        assert ret == 0, f'Error, code: {ret}'

    def tick(self) -> None:
        self.__dll.tick_all()

class UnidriverDeviceFabric:
    class EndLine(IntEnum):
        CR_LF = 0
        CR = 1
        LF = 2
        NONE = 3

    class MultimeterModes(IntEnum):
        ACTIVE = 0
        PASSIVE = 1

    class RefreshModes(IntEnum):
        INVALID = 0
        AUTO = 1
        MANUAL = 2

    def __init__(self, dll_wrapper: UnidriverDLLWrapper) -> None:
        self.__dll = dll_wrapper.dll

    # Добавить функции для работы с counter
    def create_modbus_udp_client(self, ip: str, port: str,
                                 refresh_mode: RefreshModes = RefreshModes.AUTO,
                                 discr_inputs_size_byte: int = 8, coils_size_byte: int = 8,
                                 hold_regs_reg: int = 7, input_regs_reg: int = 7,
                                 update_time: int = 200, device_name: str = 'modbus udp client') -> Device:
        ip_buf = ctypes.create_string_buffer(ip.encode('utf-8'))
        port_buf = ctypes.create_string_buffer(port.encode('utf-8'))
        flow_handle = self.__dll.create_udp_client_flow(ip_buf, port_buf)
        assert flow_handle >= 0, f'Flow not created, code: {flow_handle}'
        device_handle = self.__dll.create_modbus_client(flow_handle, refresh_mode,
                                                        discr_inputs_size_byte,
                                                        coils_size_byte, hold_regs_reg,
                                                        input_regs_reg, update_time)
        assert device_handle >= 0, f'Device not created, code: {flow_handle}'
        return Device(handle=device_handle, name=device_name)


class UnidriverDeviceBuilder:
    def __init__(self, dll_initializer: UnidriverDLLWrapper) -> None:
        self.__dll = dll_initializer.dll
