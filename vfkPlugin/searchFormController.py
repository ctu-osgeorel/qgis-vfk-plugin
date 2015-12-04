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

from PyQt4.QtCore import QObject, QUrl, QRegExp, SIGNAL, SLOT
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

    def __init__(self, mainControls, searchForms, parent):

        super(SearchFormController, self).__init__()

        self.controls = self.MainControls
        self.forms = self.SearchForms
        self.mConnectionName = ""

        self.mDruhParcely = VfkTableModel()
        self.mDruhPozemkoveParcely = VfkTableModel()
        self.mDruhStavebniParcely = VfkTableModel()
        self.mZpusobVyuzitiBudovy = VfkTableModel()
        self.mZpusobVyuzitiJednotek = VfkTableModel()

        vla = QObject().trUtf8("vlastniky")
        par = QObject().trUtf8("parcely")
        bud = QObject().trUtf8("budovy")
        jed = QObject().trUtf8("jednotky")

        # self.controls.formCombobox.addItem(QIcon(), self.Form.Vlastnici)
        # self.controls.formCombobox.addItem(par, self.Form.Parcely)
        # self.controls.formCombobox.addItem(bud, self.Form.Budovy)
        # self.controls.formCombobox.addItem(jed, self.Form.Jednotky)

        #self.connect(self.controls.formCombobox, SIGNAL("activated(int)"), self.controls.searchForms, SLOT("setCurrentIndex(int)"))
        #self.connect(self.controls.searchButton, SIGNAL("clicked()"), self, SLOT("search()"))

        #self.controls.searchForms.setCurrentIndex(0)
        #self.controls.searchButton.setEnabled(False)

    def setConnectionName(self, connectionName):
        self.mConnectionName = connectionName
        self.initComboBoxModels()
        self.controls.searchButton.setEnabled(True)

    def initComboBoxModels(self):
        mDruhParcely = VfkTableModel(self.mConnectionName)
        pass