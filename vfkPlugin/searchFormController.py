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
        """

        :param connectionName:
        """
        self.__mConnectionName = connectionName
        self.initComboBoxModels()
        self.__controls.searchButton.setEnabled(True)

    def initComboBoxModels(self):
        """

        """
        self.__mDruhParcely = VfkTableModel(self.__mConnectionName)
        self.__mDruhParcely.druhyPozemku()

        self.__mDruhPozemkoveParcely = VfkTableModel(self.__mConnectionName)
        self.__mDruhPozemkoveParcely.druhyPozemku(True, False)

        self.__mDruhStavebniParcely = VfkTableModel(self.__mConnectionName)
        self.__mDruhStavebniParcely.druhyPozemku(False, True)

        self.__mZpusobVyuzitiBudovy = VfkTableModel(self.__mConnectionName)
        self.__mZpusobVyuzitiBudovy.zpusobVyuzitiBudov()

        self.__mZpusobVyuzitiJednotek = VfkTableModel(self.__mConnectionName)
        self.__mZpusobVyuzitiJednotek.zpusobVyuzitiJednotek()

        falseKodForDefaultDruh = ""
        text = u'libovolný'
        fakeRow = [falseKodForDefaultDruh, text]

        self.__forms.parcely.setDruhPozemkuModel(self.addFirstRowToModel(self.__mDruhParcely, fakeRow))
        self.__forms.parcely.setDruhPozemkuPozemkovaModel(self.addFirstRowToModel(self.__mDruhPozemkoveParcely, fakeRow))
        self.__forms.parcely.setDruhPozemkuStavebniModel(self.__mDruhStavebniParcely)
        self.__forms.budovy.setZpusobVyuzitiModel(self.addFirstRowToModel(self.__mZpusobVyuzitiBudovy, fakeRow))
        self.__forms.jednotky.setZpusobVyuzitiModel(self.addFirstRowToModel(self.__mZpusobVyuzitiJednotek, fakerow))

    def search(self):
        """

        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        if int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Parcely:
            self.searchParcely()
        elif int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Budovy:
            self.searchBudovy()
        elif int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Jednotky:
            self.searchJednotky()
        elif int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Vlastnici:
            self.searchVlastnici()
        else:
            pass

        QApplication.restoreOverrideCursor()

    def searchVlastnici(self):
        """

        """
        jmeno = self.__forms.vlastnici.jmeno()
        rcIco = self.__forms.vlastnici.rcIco()
        lv = self.__forms.vlastnici.lv()
        sjm = self.__forms.vlastnici.isSjm()
        opo = self.__forms.vlastnici.isOpo()
        ofo = self.__forms.vlastnici.isOfo()

        url = QUrl("showText?page=search&type=vlastnici&jmeno={}&rcIco={}&sjm={}&opo={}&ofo={}&lv={}"
                   .format(jmeno, rcIco, 1 if sjm is not None else 0, 1 if opo is not None else 0,
                           1 if ofo is not None else 0, lv))
        self.actionTriggered.emit(url)

    def searchParcely(self):
        """

        """
        parcelniCislo = self.__forms.parcely.parcelniCislo()
        typ = int(self.__forms.parcely.typParcely())
        druh = self.__forms.parcely.druhPozemkuKod()
        lv = self.__forms.parcely.lv()

        url = QUrl("showText?page=search&type=parcely&parcelniCislo={}&typ={}&druh={}&lv={}"
                   .format(parcelniCislo, typ, druh, lv))
        self.actionTriggered.emit(url)

    def searchBudovy(self):
        """

        """
        domovniCislo = self.__forms.budovy.domovniCislo()
        naParcele = self.__forms.budovy.naParcele()
        zpusobVyuziti = self.__forms.budovy.zpusobVyuzitiKod()
        lv = self.__forms.budovy.lv()

        url = QUrl("showText?page=search&type=budovy&domovniCislo={}&naParcele={}&zpusobVyuziti={}&lv={}"
                   .format(domovniCislo, naParcele, zpusobVyuziti, lv))
        self.actionTriggered.emit(url)

    def searchJednotky(self):
        """

        """
        cisloJednotky = self.__forms.jednotky.cisloJednotky()
        domovniCislo = self.__forms.jednotky.domovniCislo()
        naParcele = self.__forms.jednotky.naParcele()
        zpusobVyuziti = self.__forms.jednotky.zpusobVyuzitiKod()
        lv = self.__forms.jednotky.lv()

        url = QUrl("showText?page=search&type=jednotky&cisloJednotky={}&domovniCislo={}&naParcele={}&zpusobVyuziti={}&lv={}"
                   .format(cisloJednotky, domovniCislo, naParcele, zpusobVyuziti, lv))
        self.actionTriggered.emit(url)

    def addFirstRowToModel(self, oldModel, newRow):
        """

        :param oldModel: QAbstractItemModel
        :param newRow:
        :return:
        """
        oldModel = QAbstractItemModel(oldModel)

        model = QStandardItemModel()
        items = []

        for str in newRow:
            items.append(QStandardItem(str))

        model.appendRow(items)

        for i, row in enumerate(oldModel):
            items = []

            for j, column in enumerate(row):
                index = oldModel.index(i, j)
                data = oldModel.data(index)
                item = QStandardItem(str(data))
                items.append(item)

            model.appendRow(items)

        return model
