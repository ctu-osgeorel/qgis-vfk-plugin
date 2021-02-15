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
from qgis.PyQt.QtCore import QAbstractItemModel, QModelIndex

from .ui_jednotkysearchform import *


class JednotkySearchForm(QWidget):

    def __init__(self, parent=None):
        super(JednotkySearchForm, self).__init__(parent)

        # Set up the user interface from Designer.
        self.ui = Ui_JednotkySearchForm()
        self.ui.setupUi(self)

        self.__mZpusobVyuzitiModel = QAbstractItemModel

    def cisloJednotky(self):
        return str(self.ui.mCisloJednotkyLineEdit.text()).strip()

    def domovniCislo(self):
        return str(self.ui.mCisloDomovniLineEdit.text()).strip()

    def naParcele(self):
        return str(self.ui.mNaParceleLineEdit.text()).strip()

    def lv(self):
        return str(self.ui.mLvJednotkyLineEdit.text()).strip()

    def setZpusobVyuzitiModel(self, model):
        self.__mZpusobVyuzitiModel = model
        self.ui.mZpVyuzitiCombo.setModel(model)
        self.ui.mZpVyuzitiCombo.setModelColumn(1)

    def zpusobVyuzitiKod(self):
        row = self.ui.mZpVyuzitiCombo.currentIndex()
        index = QModelIndex(self.ui.mZpVyuzitiCombo.model().index(row, 1))

        if self.ui.mZpVyuzitiCombo.model().data(index) == u"libovolný":
            return u''
        else:
            return u"{}".format(self.ui.mZpVyuzitiCombo.model().data(index))
