from typing import Tuple
import logging

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget

from irspy.qt.custom_widgets.CustomLineEdit import QEditDoubleClick


class NonOverlappingPainter(QtWidgets.QStyledItemDelegate):
    def __init__(self, a_parent=None):
        super().__init__(a_parent)

    def paint(self, painter: QtGui.QPainter, option, index: QtCore.QModelIndex):
        background = index.data(QtCore.Qt.BackgroundRole)
        if isinstance(background, QtGui.QBrush):
            if background.color() != QtCore.Qt.white:
                # WARNING Чтобы drawText работал правильно, нужно чтобы в ui форме в QTable
                # был явно прописан размер шрифта!!!
                painter.fillRect(option.rect, background)
                text_rect = option.rect
                # Не знаю как получить нормальный прямоугольник для отрисовки текста, поэтому только так
                text_rect.setLeft(text_rect.left() + 3)
                painter.drawText(text_rect, option.displayAlignment, index.data())
            else:
                super().paint(painter, option, index)
        else:
            super().paint(painter, option, index)


class TransparentPainterForView(QtWidgets.QStyledItemDelegate):
    def __init__(self, a_parent=None, a_default_color="#f5f0f0"):
        super().__init__(a_parent)
        self.color_default = QtGui.QColor(a_default_color)

    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            option.palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
            color = self.combineColors(self.color_default, self.background(option, index))
            option.palette.setColor(QtGui.QPalette.Highlight, color)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def background(self, option, index):
        background = index.data(QtCore.Qt.BackgroundRole)
        if background != QtGui.QBrush():
            return background.color()
        if self.parent().alternatingRowColors():
            if index.row() % 2 == 1:
                return option.palette.color(QtGui.QPalette.AlternateBase)
        return option.palette.color(QtGui.QPalette.Base)

    @staticmethod
    def combineColors(c1, c2):
        c3 = QtGui.QColor()
        c3.setRed((c1.red() + c2.red()) / 2)
        c3.setGreen((c1.green() + c2.green()) / 2)
        c3.setBlue((c1.blue() + c2.blue()) / 2)
        return c3


class TransparentPainterForWidget(TransparentPainterForView):
    def __init__(self, a_parent=None, a_default_color="#f5f0f0"):
        super().__init__(a_parent, a_default_color)
        self.color_default = QtGui.QColor(a_default_color)

    def background(self, option, index):
        item = self.parent().itemFromIndex(index)
        if item:
            if item.background() != QtGui.QBrush():
                return item.background().color()
        if self.parent().alternatingRowColors():
            if index.row() % 2 == 1:
                return option.palette.color(QtGui.QPalette.AlternateBase)
        return option.palette.color(QtGui.QPalette.Base)


class TableEditDoubleClick(QtWidgets.QItemDelegate):
    def __init__(self, a_parent):
        super().__init__(a_parent)

    def createEditor(self, parent: QWidget, option, index: QtCore.QModelIndex) -> QWidget:
        return QEditDoubleClick(parent)


class NonOverlappingDoubleClick(NonOverlappingPainter, TableEditDoubleClick):
    def __init__(self, a_parent):
        super().__init__(a_parent)


class ComboboxIgnoreWheel(QtWidgets.QComboBox):
    def __init__(self, a_parent):
        super().__init__(a_parent)

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        e.ignore()


class ComboboxCellDelegate(QtWidgets.QItemDelegate):
    def __init__(self, a_parent: QtCore.QObject, a_values: Tuple):
        super().__init__(a_parent)
        self.cb_values = a_values

    def createEditor(self, parent: QWidget, option, index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        editor = ComboboxIgnoreWheel(parent)
        for val in self.cb_values:
            editor.addItem(val)
        editor.setCurrentText(index.data())
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        editor.setCurrentText(index.data())
