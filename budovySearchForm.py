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
from builtins import str

from qgis.PyQt import QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.PyQt.QtCore import QAbstractItemModel

from .ui_budovysearchform import *


class BudovySearchForm(QWidget):

    def __init__(self, parent=None):
        super(BudovySearchForm, self).__init__(parent)

        # Set up the user interface from Designer.
        self.ui = Ui_BudovySearchForm()
        self.ui.setupUi(self)

        self.__mZpusobVyuzitiModel = QAbstractItemModel

    def domovniCislo(self):
        return str(self.ui.cisloDomovniLineEdit.text()).strip()

    def naParcele(self):
        return str(self.ui.naParceleLineEdit.text()).strip()

    def lv(self):
        return str(self.ui.lvBudovyLineEdit.text()).strip()

    def setZpusobVyuzitiModel(self, model):
        """

        :param model: QAbstractItemModel
        """
        self.__mZpusobVyuzitiModel = model
        self.ui.mZpVyuzitiCombo.setModel(model)
        self.ui.mZpVyuzitiCombo.setModelColumn(1)

    def zpusobVyuzitiKod(self):
        row = self.ui.mZpVyuzitiCombo.currentIndex()
        index = self.ui.mZpVyuzitiCombo.model().index(row, 1)
        if self.ui.mZpVyuzitiCombo.model().data(index) == u"libovolný":
            return u''
        else:
            return u"{}".format(self.ui.mZpVyuzitiCombo.model().data(index))
