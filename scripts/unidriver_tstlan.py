from pathlib import Path
from dotenv import load_dotenv
import sys

SRC_FOLDER = Path(__file__).resolve().parent.parent
load_dotenv(SRC_FOLDER / 'irspy' / '.env')
sys.path.append(SRC_FOLDER.as_posix())

import traceback
from PyQt5.QtWidgets import QApplication
from irspy.qt.ui_to_py import convert_ui, create_translate, convert_resources, compile_ts
from irspy.unidriver.unidriver import UnidriverDLLWrapper, UnidriverDeviceBuilder, UnidriverScheme, UnidriverIO

GUI_TEST_FOLDER = f'{SRC_FOLDER}/irspy/unidriver/gui_test'
convert_resources(f'{SRC_FOLDER}/irspy/qt/resources', f'{GUI_TEST_FOLDER}/ui/resources')
convert_ui(f'{GUI_TEST_FOLDER}/ui/', f'{GUI_TEST_FOLDER}/ui/py',
           resources_path='irspy.unidriver.gui_test.ui.resources')
create_translate(f'{GUI_TEST_FOLDER}/', f'{GUI_TEST_FOLDER}/ui/translations/en.ts', True)
compile_ts(f'{GUI_TEST_FOLDER}/ui/translations', f'{GUI_TEST_FOLDER}/ui/translations')
from irspy.unidriver.gui_test.widgets import MainWidget



def excepthook(exc_type, exc_value, exc_tb) -> None:  # type: ignore
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"!!! UNHANDLED EXCEPTION !!!\n {tb}")
    QApplication.quit()


def main() -> int:
    sys.excepthook = excepthook
    unidriver_dll = UnidriverDLLWrapper()
    dev_builder = UnidriverDeviceBuilder(unidriver_dll)
    dev_io = UnidriverIO(unidriver_dll)
    scheme = UnidriverScheme(unidriver_dll)

    qapp = QApplication(sys.argv)
    qapp.setStyle("Fusion")
    widget = MainWidget(dev_builder, dev_io, scheme)
    widget.show()
    return qapp.exec()


if __name__ == '__main__':
    main()
