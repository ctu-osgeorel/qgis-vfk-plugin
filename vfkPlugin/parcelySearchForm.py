# -*- coding: utf-8 -*-

"""
/***************************************************************************
 vfkPluginDialog
                                 A QGIS plugin
 Plugin umoznujici praci s daty katastru nemovitosti
                             -------------------
        begin                : 2015-06-11
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Stepan Bambula
        email                : stepan.bambula@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QRegExp

from ui_parcelysearchform import *


class ParcelySearchForm(QWidget):
    def __init__(self):
        # Set up the user interface from Designer.
        self.ui = Ui_ParcelySearchForm()
        self.ui.setupUi(self)

        self.__defaultModel = QAbstractItemModel()
        self.__stavebniModel = QAbstractItemModel()
        self.__pozemkovaModel = QAbstractItemModel()

        self.ui.typParcelyCombo.currentIndexChanged[str].connect(self.setDruhModel)
        self.rx = QRegExp("[0-9]*/?[0-9]*")
        self.validator = QValidator(QRegExpValidator(self.rx, self))
        self.ui.parCisloLineEdit.setValidator(self.validator)

    def parcelniCislo(self):
        return str(self.ui.parCisloLineEdit.text()).strip()

    def lv(self):
        return str(self.ui.lvParcelyLineEdit.text()).strip()

    def setDruhPozemkuModel(self, model):
        self.__defaultModel = self.__pozemkovaModel = self.__stavebniModel = model
        self.ui.druhPozemkuCombo.setModel(model)
        self.ui.druhPozemkuCombo.setModelColumn(1)

    def setDruhModel(self):
        if self.ui.typParcelyCombo.currentIndex() == 1:
            self.ui.druhPozemkuCombo.setModel(self.__pozemkovaModel)
        elif self.ui.typParcelyCombo.currentIndex() == 2:
            self.ui.druhPozemkuCombo.setModel(self.__stavebniModel)
        else:
            self.ui.druhPozemkuCombo.setModel(self.__defaultModel)

    def setDruhPozemkuStavebniModel(self, model):
        self.__stavebniModel = model

    def setDruhPozemkuPozemkovaModel(self, model):
        self.__pozemkovaModel = model

    def typParcely(self):
        return self.ui.typParcelyCombo.currentIndex()

    def druhPozemkuKod(self):
        row = int(self.ui.druhPozemkuCombo.currentIndex())
        index = QModelIndex(self.ui.druhPozemkuCombo.model().index(row, 0))
        return str(self.ui.druhPozemkuCombo.model().data(index))
