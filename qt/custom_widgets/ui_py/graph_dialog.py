# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../irspy/qt/custom_widgets/ui_forms/graph_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_graph_dialog(object):
    def setupUi(self, graph_dialog):
        graph_dialog.setObjectName("graph_dialog")
        graph_dialog.resize(567, 406)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/graph_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        graph_dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(graph_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.graph_dialog_splitter = QtWidgets.QSplitter(graph_dialog)
        self.graph_dialog_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.graph_dialog_splitter.setObjectName("graph_dialog_splitter")
        self.layoutWidget = QtWidgets.QWidget(self.graph_dialog_splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.parameters_widget = QtWidgets.QWidget(self.layoutWidget)
        self.parameters_widget.setObjectName("parameters_widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.parameters_widget)
        self.verticalLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.update_pparameters_button = QtWidgets.QPushButton(self.parameters_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.update_pparameters_button.sizePolicy().hasHeightForWidth())
        self.update_pparameters_button.setSizePolicy(sizePolicy)
        self.update_pparameters_button.setObjectName("update_pparameters_button")
        self.horizontalLayout_2.addWidget(self.update_pparameters_button)
        self.auto_update_checkbox = QtWidgets.QCheckBox(self.parameters_widget)
        self.auto_update_checkbox.setObjectName("auto_update_checkbox")
        self.horizontalLayout_2.addWidget(self.auto_update_checkbox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(self.parameters_widget)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.graphs_combobox = QtWidgets.QComboBox(self.parameters_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphs_combobox.sizePolicy().hasHeightForWidth())
        self.graphs_combobox.setSizePolicy(sizePolicy)
        self.graphs_combobox.setObjectName("graphs_combobox")
        self.horizontalLayout_5.addWidget(self.graphs_combobox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.parameters_table = QtWidgets.QTableWidget(self.parameters_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parameters_table.sizePolicy().hasHeightForWidth())
        self.parameters_table.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.parameters_table.setFont(font)
        self.parameters_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.parameters_table.setAlternatingRowColors(True)
        self.parameters_table.setWordWrap(True)
        self.parameters_table.setObjectName("parameters_table")
        self.parameters_table.setColumnCount(2)
        self.parameters_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.parameters_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.parameters_table.setHorizontalHeaderItem(1, item)
        self.parameters_table.horizontalHeader().setVisible(True)
        self.parameters_table.horizontalHeader().setDefaultSectionSize(260)
        self.parameters_table.horizontalHeader().setStretchLastSection(True)
        self.parameters_table.verticalHeader().setVisible(False)
        self.parameters_table.verticalHeader().setDefaultSectionSize(30)
        self.parameters_table.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.parameters_table)
        self.horizontalLayout.addWidget(self.parameters_widget)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.graph_dialog_splitter)
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.graph_parameters_button = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph_parameters_button.sizePolicy().hasHeightForWidth())
        self.graph_parameters_button.setSizePolicy(sizePolicy)
        self.graph_parameters_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.graph_parameters_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.graph_parameters_button.setIcon(icon1)
        self.graph_parameters_button.setIconSize(QtCore.QSize(40, 40))
        self.graph_parameters_button.setFlat(True)
        self.graph_parameters_button.setObjectName("graph_parameters_button")
        self.horizontalLayout_4.addWidget(self.graph_parameters_button)
        self.chart_layout = QtWidgets.QHBoxLayout()
        self.chart_layout.setSpacing(0)
        self.chart_layout.setObjectName("chart_layout")
        self.horizontalLayout_4.addLayout(self.chart_layout)
        self.gridLayout.addWidget(self.graph_dialog_splitter, 0, 0, 1, 1)

        self.retranslateUi(graph_dialog)
        QtCore.QMetaObject.connectSlotsByName(graph_dialog)

    def retranslateUi(self, graph_dialog):
        _translate = QtCore.QCoreApplication.translate
        graph_dialog.setWindowTitle(_translate("graph_dialog", "Графики tstlan"))
        self.update_pparameters_button.setText(_translate("graph_dialog", "Обновить"))
        self.auto_update_checkbox.setText(_translate("graph_dialog", "Обновлять автоматически"))
        self.label.setText(_translate("graph_dialog", "График:"))
        item = self.parameters_table.horizontalHeaderItem(0)
        item.setText(_translate("graph_dialog", "Параметр"))
        item = self.parameters_table.horizontalHeaderItem(1)
        item.setText(_translate("graph_dialog", "Значение"))
import icons_rc