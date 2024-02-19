from irspy.unidriver.netvar import NetVarFabric, NetVar, NetVarCTypes, NetVarIndex
from irspy.unidriver.types import ParamTypes
from irspy.unidriver.unidriver import UnidriverDLLWrapper, UnidriverDeviceBuilder, UnidriverScheme, \
    UnidriverIO, UnidriverDeviceFabric


def builder_main() -> None:
    dll_path = 'S:\\Data\\Users\\508\\Data\\Projects\\unidriver\\cmake-build-debug-cygwin\\unidriver\\cygunidriver.dll'
    unidriver_dll = UnidriverDLLWrapper(dll_path)
    dev_builder = UnidriverDeviceBuilder(unidriver_dll)
    scheme = UnidriverScheme(unidriver_dll)
    param = scheme.param(6)
    print(param, scheme.string(param.name), type(param.default))
    builder_handle = dev_builder.make_builder(0, 0)
    dev_builder.set_param(builder_handle, 0, ParamTypes.STRING, '192.168.0.86')
    dev_builder.set_param(builder_handle, 1, ParamTypes.STRING, '5006')
    dev_builder.set_param(builder_handle, 7, ParamTypes.INT32, 32)
    device_handle = dev_builder.apply(builder_handle)
    io = UnidriverIO(unidriver_dll)
    while True:
        io.tick()
        bytes_ = io.read_bytes(device_handle, 33, 1)
        print(bytes_)


def netvar_main() -> None:
    dll_path = 'S:\\Data\\Users\\508\\Data\\Projects\\unidriver\\cmake-build-debug-cygwin\\unidriver\\cygunidriver.dll'
    unidriver_dll = UnidriverDLLWrapper(dll_path)
    unidriver_io = UnidriverIO(unidriver_dll)
    dev_fabric = UnidriverDeviceFabric(unidriver_dll)
    dev = dev_fabric.create_modbus_udp_client('192.168.0.86', '5006', discr_inputs_size_byte=0,
                                              coils_size_byte=0, hold_regs_reg=20, input_regs_reg=0)
    var_fabric = NetVarFabric(unidriver_io, dev)
    var: NetVar[int] = var_fabric.make('', NetVarCTypes.U8, index=NetVarIndex(33))
    var.set(5)
    while True:
        unidriver_io.tick()


if __name__ == '__main__':
    builder_main()
    # netvar_main()
