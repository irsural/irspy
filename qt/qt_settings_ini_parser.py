from typing import Union

from PyQt5 import QtCore

from irspy.settings_ini_parser import Settings
from irspy import utils as utils


class QtSettings(Settings):
    """
    Добавляет к Settings методы для сохранения состояния и размера виджетов и состояние таблиц
    """
    def save_geometry(self, a_window_name: str, a_geometry: Union[bytes, QtCore.QByteArray]):
        self.add_ini_section(Settings.GEOMETRY_SECTION)
        self.settings[self.GEOMETRY_SECTION][a_window_name] = utils.bytes_to_base64(bytes(a_geometry))
        self.save()

    def get_last_geometry(self, a_window_name: str):
        try:
            geometry_bytes = self.settings[self.GEOMETRY_SECTION][a_window_name]
            return QtCore.QByteArray(utils.base64_to_bytes(geometry_bytes))
        except (KeyError, ValueError):
            return QtCore.QByteArray()

    def save_header_state(self, a_header_name: str, a_state: QtCore.QByteArray):
        self.add_ini_section(Settings.GEOMETRY_SECTION)
        self.settings[Settings.GEOMETRY_SECTION][a_header_name] = utils.bytes_to_base64(bytes(a_state))
        self.save()

    def get_last_header_state(self, a_header_name: str):
        try:
            state_bytes = self.settings[Settings.GEOMETRY_SECTION][a_header_name]
            return QtCore.QByteArray(utils.base64_to_bytes(state_bytes))
        except (KeyError, ValueError):
            return QtCore.QByteArray()


if __name__ == "__main__":
    # Пример использования
    import sys
    from PyQt5 import QtWidgets

    a = QtSettings("./test_settings.ini", [
        Settings.VariableInfo(a_name="list_float", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_FLOAT),
        Settings.VariableInfo(a_name="list_int", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
        Settings.VariableInfo(a_name="float1", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=123.),
        Settings.VariableInfo(a_name="int1", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=222),
        Settings.VariableInfo(a_name="str1", a_section="PARAMETERS", a_type=Settings.ValueType.STRING, a_default="haha")
    ])

    print(a.list_float, a.list_int, a.float1, a.int1, a.str1)

    a.list_float = [31., 33., 333.]
    a.list_int = [11, 2, 3]
    a.float1 = 11.
    a.int1 = 331
    a.str1 = "he1he"

    app = QtWidgets.QApplication(sys.argv)

    w = QtWidgets.QDialog()
    w.setWindowTitle('Simple')
    w.restoreGeometry(a.get_last_geometry("dialog"))
    w.exec()

    a.save_geometry("dialog", w.saveGeometry())

    print(a.list_float, a.list_int, a.float1, a.int1, a.str1)
