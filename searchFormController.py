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
from __future__ import absolute_import
from builtins import range
from builtins import object

from qgis.PyQt.QtCore import QObject, QUrl, QRegExp, QModelIndex, Qt, pyqtSignal, qDebug
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QStackedWidget, QApplication

from .vfkTableModel import *


class SearchFormController(QObject):

    class SearchForms(QStackedWidget):
        vlastnici = None
        parcely = None
        budovy = None
        jednotky = None

    class MainControls(object):
        formCombobox = None
        searchForms = None
        searchButton = None

    class Form(object):
        Vlastnici = 0
        Parcely = 1
        Budovy = 2
        Jednotky = 3

    # signals
    actionTriggered = pyqtSignal(QUrl)

    def __init__(self, mainControls, searchForms, parent=None):
        """

        :type mainControls: MainControls
        :type searchForms: SearchForms
        :type parent: QObject
        :return:
        """

        QObject.__init__(self)
        self.__controls = mainControls
        self.__forms = searchForms
        self.__mConnectionName = ''

        self.__mDruhParcely = ''
        self.__mDruhPozemkoveParcely = ''
        self.__mDruhStavebniParcely = ''
        self.__mZpusobVyuzitiBudovy = ''
        self.__mZpusobVyuzitiJednotek = ''

        self.__controls.formCombobox.addItem(u"vlastníky", self.Form.Vlastnici)
        self.__controls.formCombobox.addItem(u"parcely", self.Form.Parcely)
        self.__controls.formCombobox.addItem(u"budovy", self.Form.Budovy)
        self.__controls.formCombobox.addItem(u"jednotky", self.Form.Jednotky)
		
        self.__controls.formCombobox.activated.connect(self.__controls.searchForms.setCurrentIndex)
		
        self.__controls.searchButton.clicked.connect(self.search)

        self.__controls.searchForms.setCurrentIndex(0)
        self.__controls.searchButton.setEnabled(False)

    def setConnectionName(self, connectionName):
        """

        :type connectionName: str
        """
        self.__mConnectionName = connectionName
        self.__initComboBoxModels()
        self.__controls.searchButton.setEnabled(True)

    def search(self):
        """

        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        if int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Parcely:
            self.__searchParcely()
        elif int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Budovy:
            self.__searchBudovy()
        elif int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Jednotky:
            self.__searchJednotky()
        elif int(self.__controls.formCombobox.itemData(self.__controls.formCombobox.currentIndex())) == self.Form.Vlastnici:
            self.__searchVlastnici()
        else:
            qDebug("Neplatna hodnota v SearchComboBoxu!!!")

        QApplication.restoreOverrideCursor()

    def __searchVlastnici(self):
        """

        """
        jmeno = self.__forms.vlastnici.jmeno()
        rcIco = self.__forms.vlastnici.rcIco()
        lv = self.__forms.vlastnici.lv()
        sjm = self.__forms.vlastnici.isSjm()
        opo = self.__forms.vlastnici.isOpo()
        ofo = self.__forms.vlastnici.isOfo()

        url = QUrl(u"showText?page=search&type=vlastnici&jmeno={}&rcIco={}&sjm={}&opo={}&ofo={}&lv={}"
                   .format(jmeno, rcIco, 1 if sjm else 0, 1 if opo else 0, 1 if ofo else 0, lv))
        self.actionTriggered.emit(url)

    def __searchParcely(self):
        """

        """
        parcelniCislo = self.__forms.parcely.parcelniCislo()
        typ = int(self.__forms.parcely.typParcely())
        druh = self.__forms.parcely.druhPozemkuKod()
        lv = self.__forms.parcely.lv()

        url = QUrl(u"showText?page=search&type=parcely&parcelniCislo={}&typ={}&druh={}&lv={}"
                   .format(parcelniCislo, typ, druh, lv))
        self.actionTriggered.emit(url)

    def __searchBudovy(self):
        """

        """
        domovniCislo = self.__forms.budovy.domovniCislo()
        naParcele = self.__forms.budovy.naParcele()
        zpusobVyuziti = self.__forms.budovy.zpusobVyuzitiKod()
        lv = self.__forms.budovy.lv()

        url = QUrl(u"showText?page=search&type=budovy&domovniCislo={}&naParcele={}&zpusobVyuziti={}&lv={}"
                   .format(domovniCislo, naParcele, zpusobVyuziti, lv))
        self.actionTriggered.emit(url)

    def __searchJednotky(self):
        """

        """
        cisloJednotky = self.__forms.jednotky.cisloJednotky()
        domovniCislo = self.__forms.jednotky.domovniCislo()
        naParcele = self.__forms.jednotky.naParcele()
        zpusobVyuziti = self.__forms.jednotky.zpusobVyuzitiKod()
        lv = self.__forms.jednotky.lv()

        url = QUrl(u"showText?page=search&type=jednotky&cisloJednotky={}&domovniCislo={}&naParcele={}&zpusobVyuziti={}&lv={}"
                   .format(cisloJednotky, domovniCislo, naParcele, zpusobVyuziti, lv))
        self.actionTriggered.emit(url)

    def __initComboBoxModels(self):
        """

        """
        self.__mDruhParcely = VfkTableModel(self.__mConnectionName, self)
        self.__mDruhParcely.druhyPozemku(True, True)

        self.__mDruhPozemkoveParcely = VfkTableModel(
            self.__mConnectionName, self)
        self.__mDruhPozemkoveParcely.druhyPozemku(True, False)

        self.__mDruhStavebniParcely = VfkTableModel(
            self.__mConnectionName, self)
        self.__mDruhStavebniParcely.druhyPozemku(False, True)

        self.__mZpusobVyuzitiBudovy = VfkTableModel(
            self.__mConnectionName, self)
        self.__mZpusobVyuzitiBudovy.zpusobVyuzitiBudov()

        self.__mZpusobVyuzitiJednotek = VfkTableModel(
            self.__mConnectionName, self)
        self.__mZpusobVyuzitiJednotek.zpusobVyuzitiJednotek()

        falseKodForDefaultDruh = ''
        text = u'libovolný'
        fakeRow = [falseKodForDefaultDruh, text]

        self.__forms.parcely.setDruhPozemkuModel(
            self.__addFirstRowToModel(self.__mDruhParcely, fakeRow))
        self.__forms.parcely.setDruhPozemkuPozemkovaModel(
            self.__addFirstRowToModel(self.__mDruhPozemkoveParcely, fakeRow))
        self.__forms.parcely.setDruhPozemkuStavebniModel(
            self.__mDruhStavebniParcely)
        self.__forms.budovy.setZpusobVyuzitiModel(
            self.__addFirstRowToModel(self.__mZpusobVyuzitiBudovy, fakeRow))
        self.__forms.jednotky.setZpusobVyuzitiModel(
            self.__addFirstRowToModel(self.__mZpusobVyuzitiJednotek, fakeRow))

    def __addFirstRowToModel(self, oldModel, newRow):
        """

        :type oldModel: QAbstractItemModel
        :type newRow: list
        :return: QStandardItemModel
        """
        model = QStandardItemModel(self)
        items = []

        for str in newRow:
            items.append(QStandardItem(str))

        model.appendRow(items)

        for i in range(oldModel.rowCount()):
            items = []

            for j in range(oldModel.columnCount()):
                index = QModelIndex(oldModel.index(i, j))
                data = oldModel.data(index)
                item = QStandardItem(data)
                items.append(item)

            model.appendRow(items)

        return model
