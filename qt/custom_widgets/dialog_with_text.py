from typing import List

from PyQt5 import QtGui, QtWidgets

from ui.py.dialog_with_text import Ui_Dialog as DialogForm
from irspy.qt.qt_settings_ini_parser import QtSettings


class DialogWithText(QtWidgets.QDialog):
    def __init__(self, a_text_strings: List[str], a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.ui = DialogForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.__class__.__name__))
        self.show()

        self.ui.textEdit.setText("".join(a_text_strings))

    def __del__(self):
        print("dialog with text deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.__class__.__name__, self.saveGeometry())
        a_event.accept()
