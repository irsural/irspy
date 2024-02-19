from enum import IntEnum
from typing import Dict, Any, NamedTuple, Generic, TypeVar
import struct
from irspy.unidriver.unidriver import UnidriverDLLWrapper, UnidriverIO, UnidriverDeviceFabric


class NetVarCTypes(IntEnum):
    U8 = 1
    U16 = 2
    U32 = 3
    U64 = 4
    I8 = 5
    I16 = 6
    I32 = 7
    I64 = 8
    F32 = 9
    F64 = 10
    BIT = 11


class NetVarModes(IntEnum):
    R = 0
    RW = 1


T = TypeVar('T')


class NetVarType(Generic[T], NamedTuple):
    name: str
    size: int
    pytype_fabric: type[T]
    ctype: NetVarCTypes
    format: str


_types: Dict[NetVarCTypes, NetVarType[int | float | bool]] = {
    NetVarCTypes.U8: NetVarType(name='u8', size=8, pytype_fabric=int, ctype=NetVarCTypes.U8,
                                format='B'),
    NetVarCTypes.U16: NetVarType(name='u16', size=16, pytype_fabric=int, ctype=NetVarCTypes.U16,
                                 format='H'),
    NetVarCTypes.U32: NetVarType(name='u32', size=32, pytype_fabric=int, ctype=NetVarCTypes.U32,
                                 format='I'),
    NetVarCTypes.U64: NetVarType(name='u64', size=64, pytype_fabric=int, ctype=NetVarCTypes.U64,
                                 format='Q'),
    NetVarCTypes.I8: NetVarType(name='i8', size=8, pytype_fabric=int, ctype=NetVarCTypes.I8,
                                format='b'),
    NetVarCTypes.I16: NetVarType(name='i16', size=16, pytype_fabric=int, ctype=NetVarCTypes.I8,
                                 format='h'),
    NetVarCTypes.I32: NetVarType(name='i32', size=32, pytype_fabric=int, ctype=NetVarCTypes.I16,
                                 format='i'),
    NetVarCTypes.I64: NetVarType(name='i64', size=64, pytype_fabric=int, ctype=NetVarCTypes.I32,
                                 format='q'),
    NetVarCTypes.F32: NetVarType(name='f32', size=32, pytype_fabric=float, ctype=NetVarCTypes.F32,
                                 format='f'),
    NetVarCTypes.F64: NetVarType(name='f64', size=64, pytype_fabric=float, ctype=NetVarCTypes.F64,
                                 format='d'),
    NetVarCTypes.BIT: NetVarType(name='bit', size=1, pytype_fabric=bool, ctype=NetVarCTypes.BIT,
                                 format=''),
}


class NetVarIndex(NamedTuple):
    byte_index: int
    bit_index: int | None = None


class NetVar(Generic[T]):
    def __init__(self, unidriver: UnidriverIO, name: str, device_handle: int, type_: NetVarType[T],
                 index: NetVarIndex, mode: NetVarModes) -> None:
        assert type_.ctype != NetVarCTypes.BIT or index.bit_index is not None and 0 <= index.bit_index < 8, \
            f'Invalid bit index for bit network variable, {index}, {type_.ctype.name}'
        self.__unidriver = unidriver
        self.__name = name
        self.__type = type_
        self.__index = index
        self.__mode = mode
        self.__device_handle = device_handle

    def get(self) -> T:
        if self.__type.ctype == NetVarCTypes.BIT:
            assert self.__index.bit_index is not None
            val = self.__unidriver.read_bit(self.__device_handle, self.__index.byte_index,
                                            self.__index.bit_index)
        else:
            bytes_ = self.__unidriver.read_bytes(self.__device_handle, self.__index.byte_index,
                                                 self.__type.size // 8)
            val = struct.unpack(self.__type.format, bytes_)[0]
        return self.__type.pytype_fabric(val)  # type: ignore

    def set(self, value: T) -> None:
        assert isinstance(value, self.__type.pytype_fabric)
        if self.__type.ctype == NetVarCTypes.BIT:
            assert self.__index.bit_index
            self.__unidriver.write_bit(self.__device_handle, self.__index.byte_index,
                                       self.__index.bit_index, bool(value))
        else:
            _bytes = struct.pack(self.__type.format, value)
            self.__unidriver.write_bytes(self.__device_handle, self.__index.byte_index, _bytes)

    @property
    def type(self) -> NetVarType[T]:
        return self.__type

    @property
    def index(self) -> NetVarIndex:
        return self.__index


class NetVarRepo(Dict[NetVarIndex, NetVar[Any]]):
    def __init__(self) -> None:
        super().__init__()
        self.__last_index: NetVarIndex | None = None

    def __setitem__(self, key: NetVarIndex, value: NetVar[Any]) -> None:
        assert key not in self.keys(), f'Duplicate indexes, {key}, {value.type}'
        self.__last_index = key
        super().__setitem__(key, value)

    def next_index(self, type_: NetVarType[Any]) -> NetVarIndex:
        if self.__last_index is None:
            self.__last_index = NetVarIndex(0, 0 if type_.ctype == NetVarCTypes.BIT else None)
            return self.__last_index

        last_var = self[self.__last_index]
        is_last_bit = last_var.type.ctype == NetVarCTypes.BIT
        is_next_bit = type_.ctype == NetVarCTypes.BIT
        next_byte_index, next_bit_index = last_var.index

        if is_last_bit != is_next_bit:
            next_byte_index += 1
            next_bit_index = 0 if is_next_bit else None
        elif type_.ctype == NetVarCTypes.BIT:
            assert next_bit_index is not None
            if next_bit_index >= 7:
                next_bit_index = 0
                next_byte_index += 1
            else:
                next_bit_index += 1
        else:
            assert next_bit_index is None
            next_byte_index += last_var.type.size // 8

        return NetVarIndex(next_byte_index, next_bit_index)

    def append(self, net_var: NetVar[Any]) -> NetVarIndex:
        self.__last_index = self.next_index(net_var.type)
        super().__setitem__(self.__last_index, net_var)
        return self.__last_index


class NetVarFabric:
    def __init__(self, unidriver: UnidriverIO, device_handle: int) -> None:
        self.__unidriver = unidriver
        self.__device_handle = device_handle
        self.__repo = NetVarRepo()

    def make(self, name: str, type_code_: NetVarCTypes, index: NetVarIndex | None = None,
             mode: NetVarModes = NetVarModes.R) -> NetVar[Any]:
        type_ = _types[type_code_]
        if index is None:
            index = self.__repo.next_index(type_)
        net_var = NetVar(self.__unidriver, name, self.__device_handle, type_, index, mode)
        self.__repo[index] = net_var
        return net_var
