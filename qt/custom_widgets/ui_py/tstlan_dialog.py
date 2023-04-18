# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tstlan_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_tstlan_dialog(object):
    def setupUi(self, tstlan_dialog):
        tstlan_dialog.setObjectName("tstlan_dialog")
        tstlan_dialog.resize(672, 651)
        font = QtGui.QFont()
        font.setPointSize(10)
        tstlan_dialog.setFont(font)
        tstlan_dialog.setFocusPolicy(QtCore.Qt.TabFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/tstlan.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        tstlan_dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(tstlan_dialog)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.show_marked_checkbox = QtWidgets.QCheckBox(tstlan_dialog)
        self.show_marked_checkbox.setObjectName("show_marked_checkbox")
        self.gridLayout.addWidget(self.show_marked_checkbox, 1, 2, 1, 1)
        self.name_filter_edit = QtWidgets.QLineEdit(tstlan_dialog)
        self.name_filter_edit.setObjectName("name_filter_edit")
        self.gridLayout.addWidget(self.name_filter_edit, 1, 4, 1, 1)
        self.upadte_time_spinbox = QtWidgets.QDoubleSpinBox(tstlan_dialog)
        self.upadte_time_spinbox.setDecimals(1)
        self.upadte_time_spinbox.setMinimum(0.1)
        self.upadte_time_spinbox.setSingleStep(0.5)
        self.upadte_time_spinbox.setProperty("value", 1.5)
        self.upadte_time_spinbox.setObjectName("upadte_time_spinbox")
        self.gridLayout.addWidget(self.upadte_time_spinbox, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(tstlan_dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.graphs_button = QtWidgets.QPushButton(tstlan_dialog)
        self.graphs_button.setAutoDefault(False)
        self.graphs_button.setObjectName("graphs_button")
        self.gridLayout.addWidget(self.graphs_button, 1, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.variables_table = QtWidgets.QTableWidget(tstlan_dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.variables_table.setFont(font)
        self.variables_table.setObjectName("variables_table")
        self.variables_table.setColumnCount(7)
        self.variables_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.variables_table.setHorizontalHeaderItem(6, item)
        self.variables_table.horizontalHeader().setSortIndicatorShown(True)
        self.variables_table.horizontalHeader().setStretchLastSection(True)
        self.variables_table.verticalHeader().setVisible(False)
        self.variables_table.verticalHeader().setDefaultSectionSize(22)
        self.variables_table.verticalHeader().setMinimumSectionSize(22)
        self.verticalLayout.addWidget(self.variables_table)

        self.retranslateUi(tstlan_dialog)
        QtCore.QMetaObject.connectSlotsByName(tstlan_dialog)
        tstlan_dialog.setTabOrder(self.variables_table, self.upadte_time_spinbox)
        tstlan_dialog.setTabOrder(self.upadte_time_spinbox, self.show_marked_checkbox)
        tstlan_dialog.setTabOrder(self.show_marked_checkbox, self.graphs_button)
        tstlan_dialog.setTabOrder(self.graphs_button, self.name_filter_edit)

    def retranslateUi(self, tstlan_dialog):
        _translate = QtCore.QCoreApplication.translate
        tstlan_dialog.setWindowTitle(_translate("tstlan_dialog", "Tstlan"))
        self.show_marked_checkbox.setText(_translate("tstlan_dialog", "Оставить отмеченные"))
        self.name_filter_edit.setPlaceholderText(_translate("tstlan_dialog", "Поиск..."))
        self.label.setText(_translate("tstlan_dialog", "Время обновления, с"))
        self.graphs_button.setText(_translate("tstlan_dialog", "Графики"))
        self.variables_table.setSortingEnabled(True)
        item = self.variables_table.horizontalHeaderItem(0)
        item.setText(_translate("tstlan_dialog", "№"))
        item = self.variables_table.horizontalHeaderItem(1)
        item.setText(_translate("tstlan_dialog", "Индекс"))
        item = self.variables_table.horizontalHeaderItem(3)
        item.setText(_translate("tstlan_dialog", "Имя"))
        item = self.variables_table.horizontalHeaderItem(4)
        item.setText(_translate("tstlan_dialog", "Граф."))
        item = self.variables_table.horizontalHeaderItem(5)
        item.setText(_translate("tstlan_dialog", "Тип"))
        item = self.variables_table.horizontalHeaderItem(6)
        item.setText(_translate("tstlan_dialog", "Значение"))
from irspy.qt.resources import icons
