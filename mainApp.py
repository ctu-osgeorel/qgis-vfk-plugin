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

# Import the PyQt, QGIS libraries and classes
from PyQt4 import QtCore, QtGui
from re import search
import os
import csv

from PyQt4.QtGui import QMainWindow, QFileDialog, QMessageBox, QProgressDialog, QToolBar, QActionGroup, QDockWidget, QToolButton, QMenu, QPalette, QDesktopServices
from PyQt4.QtCore import QUuid, QFileInfo, QDir, Qt, QObject, QSignalMapper, SIGNAL, SLOT, pyqtSignal, qDebug, QThread, QSettings
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *
from qgis.gui import *
from osgeo import ogr, gdal
import time

from ui_MainApp import Ui_MainApp
from searchFormController import *
from openThread import *
from applyChanges import *


class VFKError(StandardError):
    pass


class VFKWarning(Warning):
    pass


class MainApp(QDockWidget, QMainWindow, Ui_MainApp):
    # signals
    goBack = pyqtSignal()
    searchOpsubByName = pyqtSignal(str)
    enableSearch = pyqtSignal(bool)
    refreshLegend = pyqtSignal(QgsMapLayer)
    ogrDatasourceLoaded = pyqtSignal(bool)

    class VfkLayer(object):
        Par = 0
        Bud = 1

    def __init__(self, iface):
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        # variables
        self.__mLastVfkFile = []
        self.__mOgrDataSource = None
        self.__mDataSourceName = ''
        self.__fileName = []
        self.__mLoadedLayers = {}
        self.__mDefaultPalette = self.vfkFileLineEdit.palette()

        # new lineEdits variables
        self.lineEditsCount = 1

        self.__browseButtons = {}
        self.__vfkLineEdits = {}

        # apply changes into main database
        self.__databases = {}
        # self.pb_applyChanges.setEnabled(False)
        self.changes_instance = ApplyChanges()

        # Connect ui with functions
        self.__createToolbarsAndConnect()

        # check GDAL version
        gdal_version = int(gdal.VersionInfo())

        if gdal_version < 2020000:
            self.actionZpracujZmeny.setEnabled(False)
            self.pb_nextFile.setEnabled(False)
            self.pb_nextFile.setToolTip(
                u'Není možné načíst více souborů, verze GDAL je nižší než 2.2.0.')
            self.actionZpracujZmeny.setToolTip(u'Zpracování změn není povoleno, verze GDAL je nižší než 2.2.0.')

        # settings
        self.loadVfkButton.setDisabled(True)

        self.searchFormMainControls = SearchFormController.MainControls()
        self.searchFormMainControls.formCombobox = self.searchCombo
        self.searchFormMainControls.searchForms = self.searchForms
        self.searchFormMainControls.searchButton = self.searchButton

        self.searchForms = SearchFormController.SearchForms()
        self.searchForms.vlastnici = self.vlastniciSearchForm
        self.searchForms.parcely = self.parcelySearchForm
        self.searchForms.budovy = self.budovySearchForm
        self.searchForms.jednotky = self.jednotkySearchForm

        # search form controller
        self.__mSearchController = SearchFormController(
            self.searchFormMainControls, self.searchForms, self)

        self.connect(self.__mSearchController, SIGNAL(
            "actionTriggered(QUrl)"), self.vfkBrowser.processAction)
        self.connect(
            self, SIGNAL("enableSearch"), self.searchButton.setEnabled)

        self.connect(self.vfkBrowser, SIGNAL("showParcely"), self.showParInMap)
        self.connect(self.vfkBrowser, SIGNAL("showBudovy"), self.showBudInMap)

        # connect lineEdits and returnPressed action
        self.connect(self.vfkFileLineEdit, SIGNAL(
            "returnPressed()"), self.loadVfkButton_clicked)
        self.connect(self.vlastniciSearchForm.ui.jmenoLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.vlastniciSearchForm.ui.rcIcoLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.vlastniciSearchForm.ui.lvVlastniciLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.connect(self.parcelySearchForm.ui.parCisloLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.parcelySearchForm.ui.lvParcelyLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.connect(self.budovySearchForm.ui.cisloDomovniLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.budovySearchForm.ui.naParceleLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.budovySearchForm.ui.lvBudovyLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.connect(self.jednotkySearchForm.ui.mCisloJednotkyLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.jednotkySearchForm.ui.mCisloDomovniLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.jednotkySearchForm.ui.mNaParceleLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.jednotkySearchForm.ui.mLvJednotkyLineEdit,
                     SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.vfkBrowser.showHelpPage()

    def browseButton_clicked(self, browseButton_id=1):
        """
        :param browseButton_id: ID of clicked browse button.
        :return:
        """
        title = u'Načti soubor VFK'
        settings = QSettings()
        lastUsedDir = str(settings.value('/UI/' + "lastVectorFileFilter" + "Dir", "."))

        loaded_file = QFileDialog.getOpenFileName(
            self, title, lastUsedDir, u'Soubory podporované ovladačem VFK GDAL (*.vfk *.db)')

        if not loaded_file:
            return
        else:
            self.__fileName.append(loaded_file)
            if browseButton_id == 1:
                self.vfkFileLineEdit.setText(self.__fileName[0])
            else:
                self.__vfkLineEdits['vfkLineEdit_{}'.format(len(self.__vfkLineEdits))].setText(
                    self.__fileName[browseButton_id - 1])

        self.loadVfkButton.setEnabled(True)

    def browserGoBack(self):
        self.vfkBrowser.goBack()

    def browserGoForward(self):
        self.vfkBrowser.goForth()

    def selectParInMap(self):
        self.showInMap(self.vfkBrowser.currentParIds(), "PAR")

    def selectBudInMap(self):
        self.showInMap(self.vfkBrowser.currentBudIds(), "BUD")

    def latexExport(self):
        fileName = QFileDialog.getSaveFileName(
            self, u"Jméno exportovaného souboru", ".tex", "LaTeX (*.tex)")
        if fileName:
            export_succesfull = self.vfkBrowser.exportDocument(
                self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Latex)
            if export_succesfull:
                self.succesfullExport("LaTeX")

    def htmlExport(self):
        fileName = QFileDialog.getSaveFileName(
            self, u"Jméno exportovaného souboru", ".html", "HTML (*.html)")
        if fileName:
            export_succesfull = self.vfkBrowser.exportDocument(
                self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Html)
            if export_succesfull:
                self.succesfullExport("HTML")

    def setSelectionChangedConnected(self, connected):
        """

        :type connected: bool
        :return:
        """
        for layer in self.__mLoadedLayers:
            id = self.__mLoadedLayers[layer]
            vectorLayer = QgsMapLayerRegistry.instance().mapLayer(id)

            if connected:
                self.connect(
                    vectorLayer, SIGNAL("selectionChanged()"), self.showInfoAboutSelection)
            else:
                self.disconnect(
                    vectorLayer, SIGNAL("selectionChanged()"), self.showInfoAboutSelection)

    def showInMap(self, ids, layerName):
        """

        :type ids: list
        :type layerName: str
        :return:
        """
        if layerName in self.__mLoadedLayers:
            id = self.__mLoadedLayers[layerName]
            vectorLayer = QgsMapLayerRegistry.instance().mapLayer(id)
            searchString = "ID IN ({})".format(", ".join(ids))
            error = ''
            fIds = self.__search(vectorLayer, searchString, error)
            if error:
                qDebug('\n (VFK) ERROR in showInMap: {}'.format(error))
                return
            else:
                vectorLayer.setSelectedFeatures(fIds)

    def __search(self, layer, searchString, error):
        """

        :type layer: QgsVectorLayer
        :type searchString: str
        :type error: str
        :return:
        """
        # parse search string and build parsed tree
        search = QgsExpression(searchString)
        rect = QgsRectangle()
        fIds = []

        if search.hasParserError():
            error += "Parsing error:" + search.parserErrorString()
            return fIds
        if not search.prepare(layer.pendingFields()):
            error + "Evaluation error:" + search.evalErrorString()

        layer.select(rect, False)
        fit = QgsFeatureIterator(layer.getFeatures())
        f = QgsFeature()

        while fit.nextFeature(f):

            if search.evaluate(f):
                fIds.append(f.id())
            # check if there were errors during evaluating
            if search.hasEvalError():
                qDebug('\n (VFK) Evaluate error: {}'.format(error))
                break

        return fIds

    def loadVfkButton_clicked(self):
        """

        """
        amendment_file = self.__checkIfAmendmentFile(self.__fileName[0])

        if amendment_file:
            new_database_name = '{}_zmeny.db'.format(os.path.basename(self.__fileName[0]).split('.')[0])
        else:
            new_database_name = '{}_stav.db'.format(os.path.basename(self.__fileName[0]).split('.')[0])

        os.environ['OGR_VFK_DB_NAME'] = os.path.join(
            os.path.dirname(os.path.dirname(self.__fileName[0])), new_database_name)
        self.__mDataSourceName = self.__fileName[0]     # os.environ['OGR_VFK_DB_NAME']

        QgsApplication.processEvents()

        self.importThread = OpenThread(self.__fileName)
        self.importThread.working.connect(self.runLoadingLayer)
        if not self.importThread.isRunning():
            self.importThread.start()

    def runLoadingLayer(self, fileName):
        """

        :return:
        """
        if fileName not in self.__mLastVfkFile:

            self.labelLoading.setText(
                u'Načítám data do SQLite databáze (může nějaký čas trvat...)')

            try:
                self.loadVfkFile(fileName)
            except VFKError as e:
                QMessageBox.critical(
                    self, u'Chyba', u'{}'.format(e), QMessageBox.Ok)
                self.emit(SIGNAL("enableSearch"), False)
                return

            self.__mLastVfkFile.append(fileName)
            self.importThread.nextLayer = False

            if fileName == self.__fileName[-1]:
                self.loadingLayersFinished()

    def loadingLayersFinished(self):
        """

        :return:
        """
        try:
            self.__openDatabase(
                os.environ['OGR_VFK_DB_NAME'])  # self.__mDataSourceName)
        except VFKError as e:
            QMessageBox.critical(
                self, u'Chyba', u'{}'.format(e), QMessageBox.Ok)
            self.emit(SIGNAL("enableSearch"), False)
            return

        self.vfkBrowser.setConnectionName(self.property("connectionName"))
        self.__mSearchController.setConnectionName(
            self.property("connectionName"))

        self.emit(SIGNAL("enableSearch"), True)
        self.__mLoadedLayers.clear()

        if self.parCheckBox.isChecked():
            self.__loadVfkLayer('PAR')
        else:
            self.__unLoadVfkLayer('PAR')

        if self.budCheckBox.isChecked():
            self.__loadVfkLayer('BUD')
        else:
            self.__unLoadVfkLayer('BUD')

        self.labelLoading.setText(u'Načítání souborů VFK bylo dokončeno.')

    def vfkFileLineEdit_textChanged(self, arg1):
        """

        :type arg1: str
        :return:
        """
        info = QFileInfo(arg1)

        if info.isFile():
            self.loadVfkButton.setEnabled(True)
            self.vfkFileLineEdit.setPalette(self.__mDefaultPalette)
        else:
            self.loadVfkButton.setEnabled(False)
            pal = QPalette(self.vfkFileLineEdit.palette())
            pal.setColor(QPalette.text(), Qt.red)
            self.vfkFileLineEdit.setPalette(pal)

    def __loadVfkLayer(self, vfkLayerName):
        """

        :type vfkLayerName: str
        :return:
        """
        qDebug("\n(VFK) Loading vfk layer {}".format(vfkLayerName))
        if vfkLayerName in self.__mLoadedLayers:
            qDebug(
                "\n(VFK) Vfk layer {} is already loaded".format(vfkLayerName))
            return

        composedURI = self.__mDataSourceName + "|layername=" + vfkLayerName
        layer = QgsVectorLayer(composedURI, vfkLayerName, "ogr")
        if not layer.isValid():
            qDebug("\n(VFK) Layer failed to load!")

        self.__mLoadedLayers[vfkLayerName] = layer.id()

        try:
            self.__setSymbology(layer)
        except VFKWarning as e:
            QMessageBox.information(self, 'Load Style', e, QMessageBox.Ok)

        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def __unLoadVfkLayer(self, vfkLayerName):
        """

        :type vfkLayerName: str
        :return:
        """
        qDebug("\n(VFK) Unloading vfk layer {}".format(vfkLayerName))

        if vfkLayerName not in self.__mLoadedLayers:
            qDebug(
                "\n(VFK) Vfk layer {} is already unloaded".format(vfkLayerName))
            return

        QgsMapLayerRegistry.instance().removeMapLayer(
            self.__mLoadedLayers[vfkLayerName])
        del self.__mLoadedLayers[vfkLayerName]

    def __setSymbology(self, layer):
        """

        :type layer: QgsVectorLayer
        :return:
        """
        name = layer.name()
        symbologyFile = ''

        if name == 'PAR':
            symbologyFile = ':/parStyle.qml'
        elif name == 'BUD':
            symbologyFile = ':/budStyle.qml'

        errorMsg, resultFlag = layer.loadNamedStyle(symbologyFile)

        if not resultFlag:
            raise VFKWarning(u'Load style: {}'.format(errorMsg))

        layer.triggerRepaint()
        self.emit(SIGNAL("refreshLegend"), layer)

    def __openDatabase(self, dbPath):
        """

        :type dbPath: str
        :return:
        """
        qDebug("\n(VFK) Open DB: {}".format(dbPath))
        if not QSqlDatabase.isDriverAvailable('QSQLITE'):
            raise VFKError(u'Databázový ovladač QSQLITE není dostupný.')

        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        db.setDatabaseName(dbPath)
        if not db.open():
            raise VFKError(u'Nepodařilo se otevřít databázi. ')

        self.setProperty("connectionName", connectionName)

    def loadVfkFile(self, fileName):
        """

        :type fileName: str
        :return:
        """
        label_text = fileName.split('/')
        label_text = '...' + label_text[-2] + '/' + label_text[-1]

        if self.__mOgrDataSource:
            self.__mOgrDataSource.Destroy()
            self.__mOgrDataSource = None

        QgsApplication.registerOgrDrivers()

        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)

        QgsApplication.processEvents()

        #os.environ['OGR_VFK_DB_READ_ALL_BLOCKS'] = 'NO'
        self.labelLoading.setText(
            u'Načítám soubor {} (může nějaký čas trvat...)'.format(label_text))

        QgsApplication.processEvents()

        self.__mOgrDataSource = ogr.Open(
            fileName, 0)   # 0 - datasource is open in read-only mode

        if not self.__mOgrDataSource:
            raise VFKError(
                u"Nelze otevřít VFK soubor '{}' jako platný OGR datasource.".format(fileName))

        layerCount = self.__mOgrDataSource.GetLayerCount()

        layers_names = []

        for i in xrange(layerCount):
            layers_names.append(
                self.__mOgrDataSource.GetLayer(i).GetLayerDefn().GetName())

        if ('PAR' not in layers_names or 'BUD' not in layers_names) and len(self.__vfkLineEdits) == 1:
            self.__dataWithoutParBud()
            self.labelLoading.setText(
                u'Data nemohla být načtena. Vstupní soubor neobsahuje bloky PAR a BUD.')
            QgsApplication.processEvents()
            return

        # load all layers
        self.progressBar.setRange(0, layerCount - 1)
        for i in xrange(layerCount):
            self.progressBar.setValue(i)
            theLayerName = self.__mOgrDataSource.GetLayer(
                i).GetLayerDefn().GetName()
            self.labelLoading.setText(
                u"VFK data {}/{}: {}".format(i + 1, layerCount, theLayerName))
            QgsApplication.processEvents()
            self.__mOgrDataSource.GetLayer(i).GetFeatureCount(True)
            time.sleep(0.02)

        self.labelLoading.setText(
            u'Soubor {} úspěšně načten.'.format(label_text))

        self.__mOgrDataSource.Destroy()
        self.__mOgrDataSource = None

    def __selectedIds(self, layer):
        """

        :type layer: QgsVectorLayer
        :return:
        """
        ids = []
        flist = layer.selectedFeatures()

        for it in flist:
            f = QgsFeature(it)
            ids.append(str(f.attribute("ID")))
        return ids

    def showInfoAboutSelection(self):
        layers = ["PAR", "BUD"]
        layerIds = {}
        for layer in layers:
            if layer in self.__mLoadedLayers:
                id = str(self.__mLoadedLayers[layer])
                vectorLayer = QgsMapLayerRegistry.instance().mapLayer(id)
                layerIds[layer] = self.__selectedIds(vectorLayer)

        self.vfkBrowser.showInfoAboutSelection(
            layerIds["PAR"], layerIds["BUD"])

    def showParInMap(self, ids):
        """

        :type ids: list
        :return:
        """
        if self.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "PAR")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "PAR")

    def showBudInMap(self, ids):
        """

        :type ids: list
        :return:
        """
        if self.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "BUD")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "BUD")

    def showOnCuzk(self):
        x = self.vfkBrowser.currentDefinitionPoint().first.split(".")[0]
        y = self.vfkBrowser.currentDefinitionPoint().second.split(".")[0]

        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(
            y, x)
        QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))

    def switchToImport(self):
        self.actionImport.trigger()

    def switchToSearch(self, searchType):
        """
        :type searchType: int
        """
        self.actionVyhledavani.trigger()
        self.searchCombo.setCurrentIndex(searchType)
        self.searchFormMainControls.searchForms.setCurrentIndex(searchType)

    def switchToChanges(self):
        """

        """
        self.actionZpracujZmeny.trigger()

    def succesfullExport(self, export_format):
        """

        :type export_format: str
        :return:
        """
        QMessageBox.information(
            self, u'Export', u"Export do formátu {} proběhl úspěšně.".format(
                export_format),
                                QMessageBox.Ok)

    def __dataWithoutParBud(self):
        """

        :type export_format: str
        :return:
        """
        QMessageBox.warning(self, u'Upozornění', u"Zvolený VFK soubor neobsahuje vrstvy s geometrií (PAR, BUD), proto nemohou "
                            u"být pomocí VFK Pluginu načtena. Data je možné načíst v QGIS pomocí volby "
                            u"'Načíst vektorovou vrstvu.'", QMessageBox.Ok)

    def __addRowToGridLayout(self):
        if len(self.__vfkLineEdits) >= 5:
            self.__maximumLineEditsReached()
            return

        # update label
        self.label.setText('VFK soubory:')

        # new layout
        horizontalLayout = QtGui.QHBoxLayout()

        # create new objects
        self.__browseButtons['browseButton_{}'.format(
            len(self.__vfkLineEdits) + 1)] = QtGui.QPushButton(u"Procházet")
        self.__vfkLineEdits['vfkLineEdit_{}'.format(
            len(self.__vfkLineEdits) + 1)] = QtGui.QLineEdit()

        horizontalLayout.addWidget(self.__vfkLineEdits[
                                   'vfkLineEdit_{}'.format(len(self.__vfkLineEdits))])
        horizontalLayout.addWidget(self.__browseButtons[
                                   'browseButton_{}'.format(len(self.__vfkLineEdits))])

        # number of lines in gridLayout
        rows_count = self.gridLayout_12.rowCount(
        )  # count of rows in gridLayout

        # export objects from gridLayout
        item_label = self.gridLayout_12.itemAtPosition(rows_count - 2, 0)
        item_par = self.gridLayout_12.itemAtPosition(rows_count - 2, 1)
        item_bud = self.gridLayout_12.itemAtPosition(rows_count - 1, 1)

        # remove objects from gridLayout
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 2, 0))
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 2, 1))
        self.gridLayout_12.removeItem(
            self.gridLayout_12.itemAtPosition(rows_count - 1, 1))

        # re-build gridLayout
        self.gridLayout_12.addLayout(horizontalLayout, rows_count - 2, 1)
        self.gridLayout_12.addItem(item_label, rows_count - 1, 0)
        self.gridLayout_12.addItem(item_par, rows_count - 1, 1)
        self.gridLayout_12.addItem(item_bud, rows_count, 1)

        self.__browseButtons['browseButton_{}'.format(len(self.__vfkLineEdits))].clicked.\
            connect(lambda: self.browseButton_clicked(
                int('{}'.format(len(self.__vfkLineEdits)))))

    def __maximumLineEditsReached(self):
        QMessageBox.information(self, u'Upozornění', u"Byl dosažen maximální počet ({}) VFK souboru pro zpracování."
                                                     u"\nNačítání dalších souborů není povoleno!".
                                format(self.lineEditsCount), QMessageBox.Ok)

    def browseDb_clicked(self, database_type):
        """
        Method run dialog for select database in widget with changes.
        According to pushButton name will fill in relevant lineEdit.
        :type database_type: str
        """
        title = u'Vyber databázi'
        settings = QSettings()
        lastUsedDir = str(settings.value('/UI/' + "lastVectorFileFilter" + "Dir", "."))

        if database_type == 'mainDb':
            self.__databases[database_type] = QFileDialog.getOpenFileName(self, title, lastUsedDir, u'Datábaze (*.db)')
            if not self.__databases[database_type]:
                return
            self.le_mainDb.setText(self.__databases[database_type])

        elif database_type == 'amendmentDb':
            self.__databases[database_type] = QFileDialog.getOpenFileName(self, title, lastUsedDir, u'Datábaze (*.db)')
            if not self.__databases[database_type]:
                return
            self.le_amendmentDb.setText(self.__databases[database_type])

        elif database_type == 'exportDb':
            title = u'Zadej jméno výstupní databáze'
            self.__databases[database_type] = QFileDialog.getSaveFileName(self, u"Jméno výstupní databáze",
                                                                          ".db", u"Databáze (*.db)")
            if not self.__databases[database_type]:
                return
            self.le_exportDb.setText(self.__databases[database_type])

        if len(self.__databases) == 3:
            self.pb_applyChanges.setEnabled(True)

    def applyChanges(self):
        """
        Method
        :return:
        """
        self.changes_instance.run(self.__databases['mainDb'],
                                  self.__databases['amendmentDb'],
                                  self.__databases['exportDb'])

    def __updateProgressBarChanges(self, iteration, table_name):
        """
        :type iteration: int
        :type table_name: str
        """
        self.progressBar_changes.setValue(iteration)
        self.l_status.setText(u'Aplikuji změny na tabulku {}...'.format(table_name))
        QgsApplication.processEvents()

    def __setRangeProgressBarChanges(self, max_range):
        """
        :type max_range: int
        """
        self.progressBar_changes.setRange(0, max_range)
        self.progressBar_changes.setValue(0)

    def __changesApplied(self):
        """
        """
        time.sleep(1)
        self.l_status.setText(u'Změny byly úspěšně aplikovány.')
        QgsApplication.processEvents()

    def __changesPreprocessingDatabase(self):
        """
        """
        self.l_status.setText(u'Připravuji výstupní databázi...')
        QgsApplication.processEvents()

    def __checkIfAmendmentFile(self, file_name):
        """

        :param file_name: Name of the input file
        :type file_name: str
        :return: bool
        """
        if file_name.endswith(".vfk"):
            with open(file_name, 'r') as f:
                vfk = csv.reader(f, delimiter=";")

                for i, row in enumerate(vfk):
                    if row[0] == '&HZMENY':
                        if int(row[1]) == 1:
                            return True
                        else:
                            return False
        else:
            print 'database'
            # TODO: dopsat kontrolu, zda se jedna o stavovou, nebo zmenovou databazi



    def __createToolbarsAndConnect(self):

        actionGroup = QActionGroup(self)
        actionGroup.addAction(self.actionImport)
        actionGroup.addAction(self.actionVyhledavani)
        actionGroup.addAction(self.actionZpracujZmeny)

        # QSignalMapper
        self.signalMapper = QSignalMapper(self)

        # connect to 'clicked' on all buttons
        self.connect(self.actionImport, SIGNAL(
            "triggered()"), self.signalMapper, SLOT("map()"))
        self.connect(self.actionVyhledavani, SIGNAL(
            "triggered()"), self.signalMapper, SLOT("map()"))
        self.connect(self.actionZpracujZmeny, SIGNAL(
            "triggered()"), self.signalMapper, SLOT("map()"))

        # setMapping on each button to the QStackedWidget index we'd like to
        # switch to
        self.signalMapper.setMapping(self.actionImport, 0)
        self.signalMapper.setMapping(self.actionVyhledavani, 2)
        self.signalMapper.setMapping(self.actionZpracujZmeny, 1)

        # connect mapper to stackedWidget
        self.connect(self.signalMapper, SIGNAL("mapped(int)"),
                     self.stackedWidget, SLOT("setCurrentIndex(int)"))
        self.actionImport.trigger()

        self.connect(self.vfkBrowser, SIGNAL(
            "switchToPanelImport"), self.switchToImport)
        self.connect(self.vfkBrowser, SIGNAL(
            "switchToPanelSearch"), self.switchToSearch)
        self.connect(self.vfkBrowser, SIGNAL(
            "switchToPanelChanges"), self.switchToChanges)

        # Browser toolbar
        # ---------------
        self.__mBrowserToolbar = QToolBar(self)
        self.connect(self.actionBack, SIGNAL(
            "triggered()"), self.vfkBrowser.goBack)
        self.connect(self.actionForward, SIGNAL(
            "triggered()"), self.vfkBrowser.goForth)

        self.connect(self.actionSelectBudInMap,
                     SIGNAL("triggered()"), self.selectBudInMap)
        self.connect(self.actionSelectParInMap,
                     SIGNAL("triggered()"), self.selectParInMap)
        self.connect(self.actionCuzkPage,
                     SIGNAL("triggered()"), self.showOnCuzk)

        self.connect(self.actionExportLatex,
                     SIGNAL("triggered()"), self.latexExport)
        self.connect(self.actionExportHtml,
                     SIGNAL("triggered()"), self.htmlExport)

        self.connect(self.actionShowInfoaboutSelection, SIGNAL(
            "toggled(bool)"), self.setSelectionChangedConnected)
        self.connect(self.actionShowHelpPage, SIGNAL(
            "triggered()"), self.vfkBrowser.showHelpPage)

        self.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

        self.__browseButtons['browseButton_1'] = self.browseButton
        self.__browseButtons['browseButton_1'].clicked.connect(
            lambda: self.browseButton_clicked(int('{}'.format(len(self.__vfkLineEdits)))))

        self.__vfkLineEdits['vfkLineEdit_1'] = self.vfkFileLineEdit

        bt = QToolButton(self.__mBrowserToolbar)
        bt.setPopupMode(QToolButton.InstantPopup)
        bt.setText("Export ")

        menu = QMenu(bt)
        menu.addAction(self.actionExportLatex)
        menu.addAction(self.actionExportHtml)
        bt.setMenu(menu)

        # add actions to toolbar icons
        self.__mBrowserToolbar.addAction(self.actionImport)
        self.__mBrowserToolbar.addAction(self.actionVyhledavani)
        self.__mBrowserToolbar.addAction(self.actionZpracujZmeny)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addAction(self.actionBack)
        self.__mBrowserToolbar.addAction(self.actionForward)
        self.__mBrowserToolbar.addAction(self.actionSelectParInMap)
        self.__mBrowserToolbar.addAction(self.actionSelectBudInMap)
        self.__mBrowserToolbar.addAction(self.actionCuzkPage)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addAction(self.actionShowInfoaboutSelection)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addWidget(bt)
        self.__mBrowserToolbar.addSeparator()
        self.__mBrowserToolbar.addAction(self.actionShowHelpPage)

        self.rightWidgetLayout.insertWidget(0, self.__mBrowserToolbar)

        # connect signals from vfkbrowser when changing history
        self.connect(self.vfkBrowser, SIGNAL(
            "currentParIdsChanged"), self.actionSelectParInMap.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL("currentBudIdsChanged"),
                     self.actionSelectBudInMap.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL(
            "historyBefore"), self.actionBack.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL(
            "historyAfter"), self.actionForward.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL(
            "definitionPointAvailable"), self.actionCuzkPage.setEnabled)

        # add toolTips
        self.pb_nextFile.setToolTip(u'Přidej další soubor VFK')
        self.parCheckBox.setToolTip(u'Načti vrstvu parcel')
        self.budCheckBox.setToolTip(u'Načti vrstvu budov')

        # add new VFK file
        self.pb_nextFile.clicked.connect(self.__addRowToGridLayout)

        # widget apply changes
        self.pb_mainDb.clicked.connect(
            lambda: self.browseDb_clicked('mainDb'))
        self.pb_amendmentDb.clicked.connect(
            lambda: self.browseDb_clicked('amendmentDb'))
        self.pb_exportDb.clicked.connect(
            lambda: self.browseDb_clicked('exportDb'))

        self.pb_applyChanges.clicked.connect(self.applyChanges)
        self.pb_applyChanges.setEnabled(False)

        self.connect(self.changes_instance, SIGNAL("maxRangeProgressBar"), self.__setRangeProgressBarChanges)
        self.connect(self.changes_instance, SIGNAL("updateStatus"), self.__updateProgressBarChanges)
        self.connect(self.changes_instance, SIGNAL("finishedStatus"), self.__changesApplied)
        self.connect(self.changes_instance, SIGNAL("preprocessingDatabase"), self.__changesPreprocessingDatabase)
