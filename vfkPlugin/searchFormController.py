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

from PyQt4.QtCore import QObject, QUrl, QRegExp, SIGNAL, SLOT, Qt, pyqtSignal
from PyQt4.QtGui import QStandardItemModel, QComboBox, QPushButton, QStackedWidget

from vlastniciSearchForm import *
from parcelySearchForm import *
from budovySearchForm import *
from jednotkySearchForm import *
from vfkTableModel import *


class VlastniciSearchForm:
    pass

class ParcelySearchForm:
    pass

class BudovySearchForm:
    pass

class JednotkySearchForm:
    pass


class SearchFormController(QObject):
    class SearchForms:
        vlastnici = VlastniciSearchForm
        parcely = ParcelySearchForm
        budovy = BudovySearchForm
        jednotky = JednotkySearchForm

    class MainControls:
        formCombobox = QComboBox
        searchForms = QStackedWidget
        searchButton = QPushButton

    class Form(object):
        Vlastnici = 0
        Parcely = 1
        Budovy = 2
        Jednotky = 3

    # signals
    actionTriggered = pyqtSignal(QUrl)

    def __init__(self, mainControls, searchForms, parent):

        super(SearchFormController, self).__init__()

        self.__controls = self.MainControls()
        self.__forms = self.SearchForms()
        self.__mConnectionName = ""

        self.__mDruhParcely = VfkTableModel()
        self.__mDruhPozemkoveParcely = VfkTableModel()
        self.__mDruhStavebniParcely = VfkTableModel()
        self.__mZpusobVyuzitiBudovy = VfkTableModel()
        self.__mZpusobVyuzitiJednotek = VfkTableModel()

        self.__controls.formCombobox.addItem(QObject.trUtf8(self, "vlastníky" ), self.Form.Vlastnici)
        self.__controls.formCombobox.addItem(QObject.trUtf8(self, "parcely"), self.Form.Parcely)
        self.__controls.formCombobox.addItem(QObject.trUtf8(self, "budovy"), self.Form.Budovy)
        self.__controls.formCombobox.addItem(QObject.trUtf8(self, "jednotky"), self.Form.Jednotky)

        self.connect(self.__controls.formCombobox, SIGNAL("activated(int)"), self.__controls.searchForms, SLOT("setCurrentIndex(int)"))
        self.connect(self.__controls.searchButton, SIGNAL("clicked()"), self, SLOT("search()"))

        self.__controls.searchForms.setCurrentIndex(0)
        self.__controls.searchButton.setEnabled(False)

    def setConnectionName(self, connectionName):
        self.mConnectionName = connectionName
        self.initComboBoxModels()
        self.controls.searchButton.setEnabled(True)

    def initComboBoxModels(self):
        mDruhParcely = VfkTableModel(self.mConnectionName)
        pass

    def search(self):
        form = self.Form()