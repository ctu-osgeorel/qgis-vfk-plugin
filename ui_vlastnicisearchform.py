from builtins import object
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_vlastnicisearchform.ui'
#
# Created: Fri Nov 20 17:51:01 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_VlastniciSearchForm(object):

    def setupUi(self, VlastniciSearchForm):
        VlastniciSearchForm.setObjectName(_fromUtf8("VlastniciSearchForm"))
        VlastniciSearchForm.resize(238, 208)
        self.gridLayout = QtWidgets.QGridLayout(VlastniciSearchForm)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtWidgets.QLabel(VlastniciSearchForm)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.jmenoLineEdit = QtWidgets.QLineEdit(VlastniciSearchForm)
        self.jmenoLineEdit.setObjectName(_fromUtf8("jmenoLineEdit"))
        self.gridLayout.addWidget(self.jmenoLineEdit, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(VlastniciSearchForm)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.ofoCheckBox = QtWidgets.QCheckBox(VlastniciSearchForm)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ofoCheckBox.sizePolicy().hasHeightForWidth())
        self.ofoCheckBox.setSizePolicy(sizePolicy)
        self.ofoCheckBox.setChecked(True)
        self.ofoCheckBox.setObjectName(_fromUtf8("ofoCheckBox"))
        self.gridLayout.addWidget(self.ofoCheckBox, 1, 1, 1, 1)
        self.opoCheckBox = QtWidgets.QCheckBox(VlastniciSearchForm)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.opoCheckBox.sizePolicy().hasHeightForWidth())
        self.opoCheckBox.setSizePolicy(sizePolicy)
        self.opoCheckBox.setChecked(True)
        self.opoCheckBox.setObjectName(_fromUtf8("opoCheckBox"))
        self.gridLayout.addWidget(self.opoCheckBox, 2, 1, 1, 1)
        self.sjmCheckBox = QtWidgets.QCheckBox(VlastniciSearchForm)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sjmCheckBox.sizePolicy().hasHeightForWidth())
        self.sjmCheckBox.setSizePolicy(sizePolicy)
        self.sjmCheckBox.setChecked(True)
        self.sjmCheckBox.setObjectName(_fromUtf8("sjmCheckBox"))
        self.gridLayout.addWidget(self.sjmCheckBox, 3, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(VlastniciSearchForm)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.rcIcoLineEdit = QtWidgets.QLineEdit(VlastniciSearchForm)
        self.rcIcoLineEdit.setObjectName(_fromUtf8("rcIcoLineEdit"))
        self.gridLayout.addWidget(self.rcIcoLineEdit, 4, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(VlastniciSearchForm)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.lvVlastniciLineEdit = QtWidgets.QLineEdit(VlastniciSearchForm)
        self.lvVlastniciLineEdit.setObjectName(
            _fromUtf8("lvVlastniciLineEdit"))
        self.gridLayout.addWidget(self.lvVlastniciLineEdit, 5, 1, 1, 1)

        self.retranslateUi(VlastniciSearchForm)
        QtCore.QMetaObject.connectSlotsByName(VlastniciSearchForm)

    def retranslateUi(self, VlastniciSearchForm):
        VlastniciSearchForm.setWindowTitle(
            _translate("VlastniciSearchForm", "Form", None))
        self.label.setText(_translate("VlastniciSearchForm", "Jméno:", None))
        self.label_4.setText(
            _translate("VlastniciSearchForm", "Typ osoby:", None))
        self.ofoCheckBox.setText(
            _translate("VlastniciSearchForm", "OFO", None))
        self.opoCheckBox.setText(
            _translate("VlastniciSearchForm", "OPO", None))
        self.sjmCheckBox.setText(
            _translate("VlastniciSearchForm", "SJM", None))
        self.label_2.setText(
            _translate("VlastniciSearchForm", "RČ/IČO:", None))
        self.label_3.setText(_translate("VlastniciSearchForm", "LV:", None))
