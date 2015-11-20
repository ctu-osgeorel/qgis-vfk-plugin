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
from PyQt4.QtCore import QAbstractItemModel, QModelIndex

from ui_budovysearchform import *


class BudovySearchForm(QWidget, Ui_BudovySearchForm):
    def __init__(self):
        self.__mZpusobVyuzitiModel = QAbstractItemModel()

    def domovniCislo(self):
        return str(self.cisloDomovniLineEdit.text()).strip()

    def naParcele(self):
        return str(self.naParceleLineEdit.text()).strip()

    def lv(self):
        return str(self.lvBudovyLineEdit.text()).strip()

    def setZpusobVyuzitiModel(self, model):
        self.__mZpusobVyuzitiModel = QAbstractItemModel(model)
        self.mZpVyuzitiCombo.setModel(model)
        self.mZpVyuzitiCombo.setModelColumn(1)

    def zpusobVyuzitiKod(self):
        row = self.mZpVyuzitiCombo.currentIndex()
        index = QModelIndex(self.mZpVyuzitiCombo.model().index(row, 0))
        return str(self.mZpVyuzitiCombo.model().data(index))
