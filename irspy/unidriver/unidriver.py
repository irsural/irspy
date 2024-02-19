import ctypes
from copy import deepcopy
from enum import IntEnum, StrEnum
from itertools import chain
from typing import List, Any, Dict, Iterable, TypeVar, Generic, Optional
from pydantic import TypeAdapter
from pydantic import BaseModel


class ParamTypes(StrEnum):
    INT32 = 'int32'
    DOUBLE = 'double'
    STRING = 'string'
    COUNTER = 'counter'
    ENUM = 'enum'


T = TypeVar('T')


class ParamScheme(BaseModel, Generic[T]):
    id: int
    name: int
    type: ParamTypes
    default: Optional[T] = None
    enum_fields: Optional[Dict[str, int]] = None


class BuilderScheme(BaseModel):
    id: int
    name: int
    params: List[int]


class GroupScheme(BaseModel):
    id: int
    name: int
    builders: List[BuilderScheme]


class ErrorScheme(BaseModel):
    id: int
    name: int


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

        dll.get_scheme.restype = res_t
        dll.get_scheme.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        dll.get_errors.restype = res_t
        dll.get_errors.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        dll.get_string.restype = res_t
        dll.get_string.argtypes = [ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
        dll.get_param.restype = res_t
        dll.get_param.argtypes = [ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]

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


class UnidriverError(RuntimeError):
    def __init__(self, error_code: int) -> None:
        self.__error_code = error_code

    def __repr__(self) -> str:
        return f'Error in unidriver DLL. Code: {self.__error_code}'

    @staticmethod
    def raise_if_error(ret: int) -> int:
        if ret < 0:
            raise UnidriverError(ret)
        return ret


class UnidriverIO:
    def __init__(self, dll_wrapper: UnidriverDLLWrapper) -> None:
        self.__dll = dll_wrapper.dll

    def read_bytes(self, handle: int, index: int, size: int) -> bytes:
        assert handle >= 0
        assert index >= 0
        assert size > 0
        buf = ctypes.create_string_buffer(size)
        UnidriverError.raise_if_error(
            self.__dll.read_bytes(handle, buf, index, size))
        return buf.raw

    def write_bytes(self, handle: int, index: int, value: bytes) -> None:
        assert handle >= 0
        assert index >= 0
        assert len(value) > 0
        buf = ctypes.create_string_buffer(value)
        UnidriverError.raise_if_error(
            self.__dll.write_bytes(handle, buf, index, len(value)))

    def read_bit(self, handle: int, byte_index: int, bit_index: int) -> bool:
        assert handle >= 0
        assert byte_index >= 0
        assert 0 <= bit_index < 8
        ret = UnidriverError.raise_if_error(
            self.__dll.read_bit(handle, byte_index, bit_index))
        return bool(ret)

    def write_bit(self, handle: int, byte_index: int, bit_index: int, value: bool) -> None:
        assert handle >= 0
        assert byte_index >= 0
        assert 0 <= bit_index < 8
        UnidriverError.raise_if_error(
            self.__dll.write_bit(handle, byte_index, bit_index, value))

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

    # TODO: Добавить функции для работы с counter
    def create_modbus_udp_client(self, ip: str, port: str,
                                 refresh_mode: RefreshModes = RefreshModes.AUTO,
                                 discr_inputs_size_byte: int = 8, coils_size_byte: int = 8,
                                 hold_regs_reg: int = 7, input_regs_reg: int = 7,
                                 update_time: int = 200) -> int:
        ip_buf = ctypes.create_string_buffer(ip.encode('utf-8'))
        port_buf = ctypes.create_string_buffer(port.encode('utf-8'))
        flow_handle = UnidriverError.raise_if_error(
            self.__dll.create_udp_client_flow(ip_buf, port_buf))
        device_handle = UnidriverError.raise_if_error(
            self.__dll.create_modbus_client(flow_handle, refresh_mode,
                                            discr_inputs_size_byte,
                                            coils_size_byte, hold_regs_reg,
                                            input_regs_reg, update_time))
        return device_handle


class UnidriverDeviceBuilder:
    def __init__(self, dll_initializer: UnidriverDLLWrapper) -> None:
        self.__dll = dll_initializer.dll

    def make_builder(self, group_scheme_index: int, builder_scheme_index: int) -> int:
        builder_handle = UnidriverError.raise_if_error(
            self.__dll.builder_create(group_scheme_index, builder_scheme_index))
        return builder_handle

    def set_param(self, builder_handle: int, param_id: int, param_type: ParamTypes, value: int | float | str) -> None:
        match param_type:
            case ParamTypes.INT32:
                assert isinstance(value, int)
                UnidriverError.raise_if_error(
                    self.__dll.builder_set_param_int32(builder_handle, param_id, value))
            case ParamTypes.DOUBLE:
                assert isinstance(value, float)
                UnidriverError.raise_if_error(
                    self.__dll.builder_set_param_double(builder_handle, param_id, value))
            case ParamTypes.STRING:
                assert isinstance(value, str)
                buf_val = ctypes.create_string_buffer(value.encode('utf-8'))
                UnidriverError.raise_if_error(
                    self.__dll.builder_set_param_u8str(builder_handle, param_id, buf_val, len(buf_val)))
            case ParamTypes.COUNTER:
                assert isinstance(value, int)
                UnidriverError.raise_if_error(
                    self.__dll.builder_set_param_counter(builder_handle, param_id, value))
            case ParamTypes.ENUM:
                assert isinstance(value, int)
                UnidriverError.raise_if_error(
                    self.__dll.builder_set_param_enum(builder_handle, param_id, value))
            case _:
                raise ValueError('Unexpected param type')

    def apply(self, builder_handle: int) -> int:
        device_handle = UnidriverError.raise_if_error(
            self.__dll.builder_apply(builder_handle))
        return device_handle


class UnidriverScheme:
    BUFFER_SIZE = 1024 * 1024

    def __init__(self, dll_initializer: UnidriverDLLWrapper) -> None:
        self.__dll = dll_initializer.dll
        self.__buf = ctypes.create_string_buffer(self.BUFFER_SIZE)

        group_ta = TypeAdapter(List[GroupScheme])
        self.__groups = group_ta.validate_json(self.__load_scheme())
        errors_ta = TypeAdapter(List[ErrorScheme])
        self.__errors = errors_ta.validate_json(self.__load_errors())
        self.__params: Dict[int, ParamScheme[Any]] = {}

    def __load_scheme(self) -> bytes:
        char_size = UnidriverError.raise_if_error(
            self.__dll.get_scheme(self.__buf, len(self.__buf)))
        return self.__buf.raw[0:char_size]

    def __load_errors(self) -> bytes:
        char_size = UnidriverError.raise_if_error(
            self.__dll.get_errors(self.__buf, len(self.__buf)))
        return self.__buf.raw[0:char_size]

    def __load_param(self, param_id: int) -> bytes:
        char_size = UnidriverError.raise_if_error(
            self.__dll.get_param(param_id, self.__buf, len(self.__buf)))
        return self.__buf.raw[0:char_size]

    def param(self, param_id: int) -> ParamScheme[Any]:
        try:
            return deepcopy(self.__params[param_id])
        except KeyError:
            param = ParamScheme[Any].model_validate_json(self.__load_param(param_id))
            self.__params[param_id] = param
            return deepcopy(param)

    def error(self, error_id: int) -> ErrorScheme:
        return deepcopy(next(filter(lambda err: err.id == error_id, self.__errors)))

    def groups(self) -> Iterable[GroupScheme]:
        return (deepcopy(group) for group in self.__groups)

    def group(self, group_id: int) -> GroupScheme:
        return deepcopy(next(filter(lambda group: group.id == group_id, self.__groups)))

    def builder(self, builder_id: int) -> BuilderScheme:
        builders = chain(*[group.builders for group in self.__groups])
        return deepcopy(next(filter(lambda builder: builder.id == builder_id, builders)))

    def string(self, str_id: int) -> str:
        char_size = UnidriverError.raise_if_error(
            self.__dll.get_string(str_id, self.__buf, len(self.__buf)))
        bytes_ = self.__buf.raw[0:char_size]
        return bytes_[0:char_size].decode('utf-8')


