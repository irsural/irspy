import os
import sys
import traceback
from typing import Protocol, Any, Callable, Dict, List

from PyQt5.QtCore import pyqtSignal, QObject, QMetaObject, QTimer, QSettings, QTranslator, QEvent
from PyQt5.QtWidgets import QWidget, QLineEdit, QComboBox, QSpinBox, QApplication, QTableWidgetItem, \
    QMessageBox, QHeaderView, QPushButton, QLabel
from PyQt5.QtCore import Qt

from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.unidriver.netvar import NetVarFabric, NetVar, NetVarCTypes, NetVarIndex, NetVarModes, \
    NetVarRepo
from irspy.unidriver.unidriver import UnidriverDLLWrapper, UnidriverDeviceBuilder, UnidriverScheme, \
    UnidriverIO, UnidriverDeviceFabric, ParamTypes, ParamScheme, BuilderScheme, GroupScheme
from irspy.unidriver.gui_test.ui.py import (builder_widget, group_widget, scheme_widget,
                                            device_io_widget, main_widget)


def make_param_widget(param: ParamScheme[Any], slot: Callable[[Any], None],
                      parent: QWidget | None = None) -> QWidget:
    match param.type:
        case ParamTypes.STRING:
            widget = TextParamWidget(param, parent)
        case ParamTypes.INT32:
            widget = IntParamWidget(param, parent)
        case ParamTypes.DOUBLE:
            raise NotImplemented
        case ParamTypes.ENUM:
            widget = EnumParamWidget(param, parent)
        case ParamTypes.COUNTER:
            widget = IntParamWidget(param, parent)
        case _:
            raise ValueError
    widget.param_changed.connect(slot)
    return widget


class TextParamWidget(QLineEdit):
    param_changed = pyqtSignal(str)

    def __init__(self, param: ParamScheme[Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.__param = param
        self.editingFinished.connect(lambda: self.param_changed.emit(self.text()))
        if self.__param.default is not None:
            self.setText(str(self.__param.default))


class IntParamWidget(QSpinBox):
    param_changed = pyqtSignal(int)

    def __init__(self, param: ParamScheme[Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMaximum(10_000_000)
        self.__param = param
        self.editingFinished.connect(lambda: self.param_changed.emit(self.value()))
        if self.__param.default is not None:
            self.setValue(self.__param.default)


class EnumParamWidget(QComboBox):
    param_changed = pyqtSignal(int)

    def __init__(self, param: ParamScheme[Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.__param = param
        assert self.__param.type == ParamTypes.ENUM, 'Not enum'
        assert self.__param.enum_fields is not None, 'Enum has no fields'
        self.__index_to_value: Dict[int, int] = {}
        for i, (name, value) in enumerate(self.__param.enum_fields.items()):
            self.__index_to_value[i] = value
            self.addItem(name)
        self.currentIndexChanged.connect(
            lambda: self.param_changed.emit(self.__index_to_value[self.currentIndex()]))


class BuilderWidget(QWidget):
    applied = pyqtSignal(int)

    def __init__(self,
                 builder_scheme: BuilderScheme,
                 unidriver_scheme: UnidriverScheme,
                 device_builder: UnidriverDeviceBuilder,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = builder_widget.Ui_BuilderWidget()
        self.ui.setupUi(self)  # type: ignore
        self.__builder_scheme = builder_scheme
        self.__unidriver_scheme = unidriver_scheme
        self.__device_builder = device_builder
        self.__handle: int | None = None
        self.__blank_params = set(self.__builder_scheme.params)
        for param_id in self.__builder_scheme.params:
            param = self.__unidriver_scheme.param(param_id)
            if param.default is not None:
                self.__blank_params.remove(param_id)

            def make_slot(param_id: int) -> Callable[[Any], None]:
                def slot(value: Any) -> None:
                    self.__param_changed(param_id, value)
                return slot

            widget = make_param_widget(param, make_slot(param_id), self)
            self.ui.form_layout.addRow(self.__unidriver_scheme.string(param.name), widget)
        self.ui.apply_btn.setEnabled(len(self.__blank_params) == 0)
        self.ui.apply_btn.clicked.connect(self.__apply)

    def __param_changed(self, param_id: int, value: Any) -> None:
        if self.__handle is None:
            self.__handle = self.__device_builder.make_builder(builder_id=self.__builder_scheme.id)
        param = self.__unidriver_scheme.param(param_id)
        self.__device_builder.set_param(self.__handle, param.id, param.type, value)
        try:
            self.__blank_params.remove(param.id)
        except KeyError:
            pass
        self.ui.apply_btn.setEnabled(len(self.__blank_params) == 0)

    def __apply(self) -> None:
        if self.__handle is None:
            assert len(self.__blank_params) == 0
            self.__handle = self.__device_builder.make_builder(builder_id=self.__builder_scheme.id)
        device_handle = self.__device_builder.apply(self.__handle)
        self.applied.emit(device_handle)
        self.__handle = None

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def retranslate_ui(self) -> None:
        self.ui.retranslateUi(self)
        for i, param_id in enumerate(self.__builder_scheme.params):
            param = self.__unidriver_scheme.param(param_id)
            string = self.__unidriver_scheme.string(param.name)
            edit: QLineEdit = self.ui.form_layout.itemAt(i * 2).widget()
            if edit:
                edit.setText(string)


class GroupWidget(QWidget):
    builder_applied = pyqtSignal(int, int)

    def __init__(self,
                 group_scheme: GroupScheme,
                 unidriver_scheme: UnidriverScheme,
                 device_builder: UnidriverDeviceBuilder,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = group_widget.Ui_group_widget()
        self.ui.setupUi(self)  # type: ignore
        self.__group_scheme = group_scheme
        self.__unidriver_scheme = unidriver_scheme
        self.__device_builder = device_builder
        for builder in self.__group_scheme.builders:
            self.ui.builders_combo.addItem(self.__unidriver_scheme.string(builder.name))
            widget = BuilderWidget(builder, self.__unidriver_scheme, self.__device_builder, self)

            def make_slot(builder_id: int) -> Callable[[int], None]:
                def slot(device_handle: int) -> None:
                    self.__builder_applied(builder_id, device_handle)
                return slot

            widget.applied.connect(make_slot(builder.id))
            self.ui.stacked_widget.addWidget(widget)
        self.ui.stacked_widget.setCurrentIndex(0)
        self.ui.builders_combo.setCurrentIndex(0)
        self.ui.builders_combo.currentIndexChanged.connect(
            lambda index: self.ui.stacked_widget.setCurrentIndex(index))

    def __builder_applied(self, builder_id: int, device_handle: int) -> None:
        self.builder_applied.emit(builder_id, device_handle)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def retranslate_ui(self) -> None:
        self.ui.retranslateUi(self)  # type: ignore
        for i, builder in enumerate(self.__group_scheme.builders):
            self.ui.builders_combo.setItemText(i, self.__unidriver_scheme.string(builder.name))

class SchemeWidget(QWidget):
    device_created = pyqtSignal(int)

    def __init__(self,
                 unidriver_scheme: UnidriverScheme,
                 device_builder: UnidriverDeviceBuilder,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = scheme_widget.Ui_scheme_widget()
        self.ui.setupUi(self)  # type: ignore
        self.__unidriver_scheme = unidriver_scheme
        self.__device_builder = device_builder
        for group in self.__unidriver_scheme.groups():
            self.ui.groups_combo.addItem(self.__unidriver_scheme.string(group.name))
            widget = GroupWidget(group, self.__unidriver_scheme, self.__device_builder, self)
            widget.builder_applied.connect(self.__builder_applied)
            self.ui.stacked_widget.addWidget(widget)
        self.ui.stacked_widget.setCurrentIndex(0)
        self.ui.groups_combo.setCurrentIndex(0)
        self.ui.groups_combo.currentIndexChanged.connect(
            lambda index: self.ui.stacked_widget.setCurrentIndex(index))

    def __builder_applied(self, builder_id: int, device_handle: int) -> None:
        print(f'Builder {builder_id} applied, device handle = {device_handle}')
        self.device_created.emit(device_handle)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def retranslate_ui(self) -> None:
        self.ui.retranslateUi(self)  # type: ignore
        for i, group in enumerate(self.__unidriver_scheme.groups()):
            self.ui.groups_combo.setItemText(i, self.__unidriver_scheme.string(group.name))


class DeviceIOWidget(QWidget):
    COL_COUNT = 2
    VALUE_COL_INDEX = 0
    COMBO_COL_INDEX = 1

    def __init__(self, dev_io: UnidriverIO, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = device_io_widget.Ui_DeviceIOWidget()
        self.ui.setupUi(self)  # type: ignore
        self.__dev_io = dev_io
        self.__dev_handle: int | None = None
        self.__var_repo: NetVarRepo | None

        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__tick)
        self.__timer.start()

        self.ui.table.setColumnCount(self.COL_COUNT)

        vheader = self.ui.table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(10)

        self.ui.table.setColumnWidth(self.COMBO_COL_INDEX, 80)
        self.ui.table.setColumnWidth(self.VALUE_COL_INDEX, 130)

        self.ui.row_cnt_spin.valueChanged.connect(self.__change_row_count)
        self.ui.row_cnt_spin.setEnabled(False)
        self.ui.load_btn.setEnabled(False)
        self.ui.save_btn.setEnabled(False)
        self.ui.load_btn.clicked.connect(self.__load)
        self.ui.save_btn.clicked.connect(self.__save)

    def __load(self) -> None:
        assert self.__var_repo is not None
        self.__var_repo.clear()
        try:
            with open(f'{os.getcwd()}/vars.txt', 'r') as file:
                for i, line in enumerate(file.readlines()):
                    type_ = NetVarCTypes(line.replace('\n', ''))
                    self.ui.table.setRowCount(self.ui.table.rowCount() + 1)
                    self.__add_row(i, type_)
            self.ui.row_cnt_spin.blockSignals(True)
            self.ui.row_cnt_spin.setValue(len(self.__var_repo))
            self.ui.row_cnt_spin.blockSignals(False)

        except Exception as ex:
            QMessageBox.critical(self, 'Error', str(ex))
            self.__var_repo.clear()

    def __save(self) -> None:
        with open(f'{os.getcwd()}/vars.txt', 'w') as file:
            for var in self.__var_repo:
                file.write(var.type.ctype)
                file.write('\n')

    def set_device_handle(self, device_handle: int) -> None:
        self.ui.row_cnt_spin.setEnabled(True)
        self.ui.load_btn.setEnabled(True)
        self.ui.save_btn.setEnabled(True)
        self.__dev_handle = device_handle
        self.__var_repo = NetVarRepo(self.__dev_io, device_handle)

    def __update_var(self, index: int, value: str) -> None:
        assert self.__var_repo is not None
        print(f'Update var {index} by {value}')
        value = self.__var_repo[index].type.pytype_fabric(value)
        self.__var_repo[index].set(value)

    # TODO: Удалять комбобоксы
    def __change_row_count(self, new_cnt: int) -> None:
        assert self.__var_repo is not None
        prev_cnt = self.ui.table.rowCount()
        self.ui.table.setRowCount(new_cnt)

        if new_cnt > prev_cnt:
            for i in range(prev_cnt, new_cnt):
                self.__add_row(i)
        else:
            self.__var_repo.pop_back(prev_cnt - new_cnt)

    def __add_row(self, index: int, type_=NetVarCTypes.U8) -> None:
        type_combo = QComboBox(self)
        for t in NetVarCTypes:
            type_combo.addItem(t)

        def make_combo_slot(row_index: int) -> Callable[[int], None]:
            def slot(type_index: int) -> None:
                # TODO: Переделать
                type_ = NetVarCTypes(list(NetVarCTypes)[type_index])
                self.__change_var_type(row_index, type_)

            return slot

        def make_edit_slot(row_index: int, edit: QLineEdit) -> Callable[[], None]:
            def slot() -> None:
                self.__update_var(row_index, edit.text())
                edit.clearFocus()

            return slot

        type_combo.setCurrentIndex(list(NetVarCTypes).index(type_))
        type_combo.currentIndexChanged.connect(make_combo_slot(index))
        self.ui.table.setCellWidget(index, self.COMBO_COL_INDEX, type_combo)
        edit = QLineEdit()
        edit.editingFinished.connect(make_edit_slot(index, edit))
        self.ui.table.setCellWidget(index, self.VALUE_COL_INDEX, edit)
        self.__var_repo.push_back(type_)

    def __change_var_type(self, var_index: int, type_: NetVarCTypes) -> None:
        assert self.__var_repo is not None
        self.__var_repo.replace(var_index, type_)

    def __tick(self) -> None:
        if self.__dev_handle is None:
            return
        self.__dev_io.tick()
        for i, netvar in enumerate(self.__var_repo):
            if i == self.ui.table.currentRow() and self.ui.table.currentColumn() == self.VALUE_COL_INDEX:
                continue
            val = netvar.get()
            edit: QLineEdit = self.ui.table.cellWidget(i, self.VALUE_COL_INDEX)
            if edit:
                edit.setText(str(val))
        connected_text = '<div><font color=\"green\">' + self.tr('ПОДКЛЮЧЕН') + '</font></div>'
        disconnected_text = '<div><font color=\"red\">' + self.tr('НЕ ПОДКЛЮЧЕН') + '</font></div>'
        self.ui.connection_lbl.setText(connected_text if self.__dev_io.is_connected(self.__dev_handle)
                                       else disconnected_text)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.ui.retranslateUi(self)  # type: ignore
        super().changeEvent(event)


class MainWidget(QWidget):
    def __init__(self,
                 dev_builder: UnidriverDeviceBuilder,
                 dev_io: UnidriverIO,
                 scheme: UnidriverScheme) -> None:
        super().__init__()
        self.ui = main_widget.Ui_MainWidget()
        self.ui.setupUi(self)  # type: ignore
        self.__scheme = scheme
        self.__scheme.set_lang('ru')
        self.__scheme_widget = SchemeWidget(scheme, dev_builder, self)
        self.__device_io_widget = DeviceIOWidget(dev_io, self)
        self.ui.hlayout.addWidget(self.__scheme_widget)
        self.ui.hlayout.addWidget(self.__device_io_widget)
        self.__scheme_widget.device_created.connect(self.__device_created)
        tr_dir = f'{os.getcwd()}/ui/translations/'
        self.__qtranslator = QTranslator(self)
        self.__langs = {'ru': '',
                        'en': f'{tr_dir}en.qm'}
        for i, (lang, tran) in enumerate(self.__langs.items()):
            self.ui.langs_combo.addItem(lang)
            self.ui.langs_combo.setItemData(i, tran)
        self.ui.langs_combo.currentIndexChanged.connect(self.__change_lang)

    def __change_lang(self) -> None:
        self.__scheme.set_lang(self.ui.langs_combo.currentText())
        if qm_file := self.ui.langs_combo.currentData():
            self.__qtranslator.load(qm_file)
            QApplication.instance().installTranslator(self.__qtranslator)
        else:
            QApplication.instance().removeTranslator(self.__qtranslator)

    def __device_created(self, device_handle: int) -> None:
        self.__device_io_widget.set_device_handle(device_handle)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.LanguageChange:
            self.ui.retranslateUi(self)  # type: ignore
        super().changeEvent(event)


def excepthook(exc_type, exc_value, exc_tb) -> None:  # type: ignore
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"!!! UNHANDLED EXCEPTION !!!\n {tb}")
    QApplication.quit()


def main() -> int:
    sys.excepthook = excepthook
    dll_path = 'S:\\Data\\Users\\508\\Data\\Projects\\unidriver\\cmake-build-debug-cygwin\\unidriver\\cygunidriver.dll'
    # unidriver_dll = UnidriverDLLWrapper(dll_path)
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
