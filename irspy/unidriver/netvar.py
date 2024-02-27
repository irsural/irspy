from abc import ABCMeta, abstractmethod
from enum import IntEnum, StrEnum
from typing import Dict, Any, NamedTuple, Generic, TypeVar, List, Iterable, Iterator
import struct
from irspy.unidriver.unidriver import UnidriverDLLWrapper, UnidriverIO, UnidriverDeviceFabric
from irspy.utils import Timer


class NetVarCTypes(StrEnum):
    U8 = 'u8'
    U16 = 'u16'
    U32 = 'u32'
    U64 = 'u64'
    I8 = 'i8'
    I16 = 'i16'
    I32 = 'i32'
    I64 = 'i64'
    F32 = 'f32'
    F64 = 'f64'
    BIT = 'bit'


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

    def __repr__(self) -> str:
        return f'{self.byte_index}' + (f'-{self.bit_index}' if self.bit_index is not None else '')


class NetVar(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> T:
        pass

    @abstractmethod
    def set(self, value: T) -> None:
        pass

    @abstractmethod
    def type(self) -> NetVarType[T]:
        pass

    @abstractmethod
    def index(self) -> NetVarIndex:
        pass

    @abstractmethod
    def set_index(self, index: NetVarIndex) -> None:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def mode(self) -> NetVarModes:
        pass


class SimpleNetVar(NetVar[T]):
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

    def type(self) -> NetVarType[T]:
        return self.__type

    def index(self) -> NetVarIndex:
        return self.__index

    def set_index(self, index: NetVarIndex) -> None:
        self.__index = index

    def name(self) -> str:
        return self.__name

    def mode(self) -> NetVarModes:
        return self.__mode


# TODO: Доделать, создать сетевые переменные с разделяемым буфером для tstLAN
class BufferedNetVar(NetVar[T]):
    def __init__(self, simple_net_var: SimpleNetVar[T], delay: int) -> None:
        self.__delay = delay
        self.__buffer: T | None = None
        self.__timer = Timer(self.__delay)
        self.__simple_net_var = simple_net_var

    def get(self) -> T:
        return self.__simple_net_var.get()

    def set(self, value: T) -> None:
        self.__simple_net_var.set(value)
        self.__buffer = value
        self.__timer.start()

    def type(self) -> NetVarType[T]:
        return self.__simple_net_var.type()

    def index(self) -> NetVarIndex:
        return self.__simple_net_var.index()

    def set_index(self, index: NetVarIndex) -> None:
        self.__simple_net_var.set_index(index)

    def name(self) -> str:
        return self.__simple_net_var.name()

    def mode(self) -> NetVarModes:
        return self.__simple_net_var.mode()


class NetVarFabric:
    def __init__(self, unidriver: UnidriverIO, device_handle: int) -> None:
        self.__unidriver = unidriver
        self.__device_handle = device_handle
        self.__last_var: NetVar[Any] | None = None

    def make(self, name: str, type_code_: NetVarCTypes, index: NetVarIndex | None | int = None,
             mode: NetVarModes = NetVarModes.R) -> SimpleNetVar[Any]:
        type_ = _types[type_code_]
        if index is None:
            index = calc_next_netvar_index(type_, self.__last_var)
        elif isinstance(index, int):
            index = NetVarIndex(index)
        net_var = SimpleNetVar(self.__unidriver, name, self.__device_handle, type_, index, mode)
        self.__last_var = net_var
        return net_var


def calc_next_netvar_index(type_: NetVarType[Any], last_var: NetVar[Any] | None = None) -> NetVarIndex:
    if last_var is None:
        return NetVarIndex(byte_index=0, bit_index=0 if type_.ctype == NetVarCTypes.BIT else None)

    is_last_bit = last_var.type().ctype == NetVarCTypes.BIT
    is_next_bit = type_.ctype == NetVarCTypes.BIT
    next_byte_index, next_bit_index = last_var.index()

    if is_last_bit and is_next_bit:
        assert next_bit_index is not None
        if next_bit_index >= 7:
            next_bit_index = 0
            next_byte_index += 1
        else:
            next_bit_index += 1
    elif is_last_bit and not is_next_bit:
        next_byte_index += 1
        next_bit_index = None
    elif not is_last_bit and is_next_bit:
        next_byte_index += last_var.type().size // 8
        next_bit_index = 0
    elif not is_last_bit and not is_next_bit:
        assert next_bit_index is None
        next_byte_index += last_var.type().size // 8
    else:
        raise ValueError

    return NetVarIndex(next_byte_index, next_bit_index)


class NetVarRepo:
    def __init__(self, unidriver: UnidriverIO, device_handle: int) -> None:
        self.__netvars: List[NetVar[Any]] = []
        self.__fabric = NetVarFabric(unidriver, device_handle)

    def push_back(self, type_code_: NetVarCTypes) -> None:
        last_var = None
        try:
            last_var = self.__netvars[-1]
        except IndexError:
            pass
        type_ = _types[type_code_]
        netvar = self.__fabric.make('', type_code_, index=calc_next_netvar_index(type_, last_var))
        self.__netvars.append(netvar)

    def replace(self, index: int, type_code_: NetVarCTypes) -> None:
        assert 0 <= index < len(self.__netvars)
        last_var = None
        if index > 0:
            last_var = self.__netvars[index-1]
        type_ = _types[type_code_]
        netvar = self.__fabric.make('', type_code_, index=calc_next_netvar_index(type_, last_var))

        self.__netvars[index] = netvar
        # for var in self.__netvars[index+1:]:
        for i in range(index, len(self.__netvars) - 1):
            prev = self.__netvars[i]
            curr = self.__netvars[i+1]
            curr.set_index(calc_next_netvar_index(curr.type(), prev))

    def clear(self) -> None:
        self.__netvars.clear()

    def pop_back(self, count: int = 1) -> None:
        if not count:
            return
        self.__netvars = self.__netvars[0:-count]

    def print(self) -> None:
        for var in self.__netvars:
            print(var.index, var.type().size)
        print('-------------')

    def __len__(self) -> int:
        return self.__netvars.__len__()

    def __getitem__(self, item: int) -> NetVar[Any]:
        return self.__netvars.__getitem__(item)

    def __iter__(self) -> Iterator[NetVar[Any]]:
        return (var for var in self.__netvars)
