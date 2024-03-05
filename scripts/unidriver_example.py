import sys
from pathlib import Path
from dotenv import load_dotenv

SRC_FOLDER = Path(__file__).resolve().parent.parent
load_dotenv(SRC_FOLDER / 'irspy' / '.env')
sys.path.append(SRC_FOLDER.as_posix())

from irspy.unidriver.netvar import NetVarFabric, NetVar, NetVarCTypes, NetVarIndex, NetVarRepo, \
    BufferedNetVar, NetVarModes
from irspy.unidriver.unidriver import UnidriverDLLWrapper, UnidriverDeviceBuilder, UnidriverScheme, \
    UnidriverIO, UnidriverDeviceFabric, ParamTypes


def builder_main() -> None:
    dll_path = 'S:\\Data\\Users\\508\\Data\\Projects\\unidriver\\cmake-build-debug-cygwin\\unidriver\\cygunidriver.dll'
    unidriver_dll = UnidriverDLLWrapper(dll_path)
    dev_builder = UnidriverDeviceBuilder(unidriver_dll)
    scheme = UnidriverScheme(unidriver_dll)
    param = scheme.param(6)
    print(param, scheme.string(param.name), type(param.default))
    builder_handle = dev_builder.make_builder(group_scheme_index=0, builder_scheme_index=0)
    dev_builder.set_param(builder_handle, 0, ParamTypes.STRING, '192.168.0.81')
    dev_builder.set_param(builder_handle, 1, ParamTypes.STRING, '5006')
    dev_builder.set_param(builder_handle, 7, ParamTypes.INT32, 32)
    device_handle = dev_builder.apply(builder_handle)
    io = UnidriverIO(unidriver_dll)
    while True:
        io.tick()
        bytes_ = io.read_bytes(device_handle, 33, 1)
        print(bytes_)


def netvar_main() -> None:
    unidriver_dll = UnidriverDLLWrapper()
    unidriver_io = UnidriverIO(unidriver_dll)
    dev_fabric = UnidriverDeviceFabric(unidriver_dll)
    dev = dev_fabric.create_modbus_udp_client('192.168.0.99', '5006', discr_inputs_size_byte=0,
                                              coils_size_byte=0, hold_regs_reg=20, input_regs_reg=0)
    # dev = dev_fabric.create_mxnet_udp_client('192.168.0.99', '5006', 100, 10_000)
    var_fabric = NetVarFabric(unidriver_io, dev)

    var: NetVar[int] = BufferedNetVar(var_fabric.make('', NetVarCTypes.U32, index=NetVarIndex(4), mode=NetVarModes.RW), 2)
    var.set(5)
    while True:
        unidriver_io.tick()
        print(var.get())


if __name__ == '__main__':
    # builder_main()
    netvar_main()
