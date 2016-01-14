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
from PyQt4.QtGui import QFileDialog, QMessageBox, QProgressDialog, QToolBar, QActionGroup
from PyQt4.QtCore import QUuid, QFileInfo, QDir, Qt, QObject, QSignalMapper, SIGNAL, SLOT, pyqtSignal, pyqtSlot, qWarning
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *
from qgis.gui import *
import ogr

from ui_MainApp import Ui_MainApp
from htmlDocument import *
from domains import *
from vfkTextBrowser import *
from searchFormController import *
from budovySearchForm import *
from jednotkySearchForm import *
from parcelySearchForm import *


class MainApp(QDockWidget, Ui_MainApp):
    # signals
    goBack = pyqtSignal()
    searchOpsubByName = pyqtSignal(str)
    enableSearch = pyqtSignal(bool)
    refreshLegend = pyqtSignal(QgsMapLayer)

    class VfkLayer(object):
        Par = 0
        Bud = 1

    def __init__(self, iface):
        QDockWidget.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface

        # variables
        self.__mLastVfkFile = ""
        self.__mOgrDataSource = None
        self.__mDataSourceName = ""
        self.__fileName = ""
        self.__mLoadedLayers = {}
        self.__mDefaultPalette = self.vfkFileLineEdit.palette()

        # Connect ui with functions
        self.__createToolbarsAndConnect()

        # settings
        self.loadVfkButton.setDisabled(True)

        self.searchFormMainControls = SearchFormController.MainControls
        self.searchFormMainControls.formCombobox = self.searchCombo
        self.searchFormMainControls.searchForms = self.searchForms
        self.searchFormMainControls.searchButton = self.searchButton

        self.searchForms = SearchFormController.SearchForms()
        self.searchForms.vlastnici = self.vlastniciSearchForm
        self.searchForms.parcely = self.parcelySearchForm
        self.searchForms.budovy = self.budovySearchForm
        self.searchForms.jednotky = self.jednotkySearchForm

        # search form controller
        self.__mSearchController = SearchFormController(self.searchFormMainControls, self.searchForms, self)

        self.connect(self.__mSearchController, SIGNAL("actionTriggered(QUrl)"), self.vfkBrowser, SLOT("processAction(QUrl)"))
        self.connect(self, SIGNAL("enableSearch(bool)"), self.searchButton, SLOT("setEnabled(bool)"))
        self.vfkBrowser.connect(self, SIGNAL("showParcely(list)"), self, SLOT("showParInMap(list)"))
        self.vfkBrowser.connect(self, SIGNAL("showBudovy(list)"), self, SLOT("showBudInMap(list)"))

        self.vfkBrowser.showHelpPage()

    def browseButton_clicked(self):
        title = u'Načti soubor VFK'
        lastUsedDir = ''
        self.__fileName = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Soubor VFK (*.vfk)')
        if self.__fileName == "":
            return
        else:
            self.vfkFileLineEdit.setText(self.__fileName)
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
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", "", "LaTeX (*.tex)")
        if fileName is not None:
            self.vfkBrowser.exportDocument(self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Latex)

    def htmlExport(self):
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", "", "HTML (*.html)")
        if fileName is not None:
            self.vfkBrowser.exportDocument(self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Html)

    def setSelectionChangedConnected(self, connected):
        for i, id in enumerate(self.__mLoadedLayers):
            vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))

            qWarning(".... setSelectionChangedConnected...........")

            if connected is True:
                self.connect(vectorLayer, SIGNAL("selectionChanged()"), self, SLOT("showInfoAboutSelection"))
            else:
                self.disconnect(vectorLayer, SIGNAL("selectionChanged()"), self, SLOT("showInfoAboutSelection"))

    def showInMap(self, ids, layerName):
        if self.__mLoadedLayers.has_key(layerName):
            id = self.__mLoadedLayers[layerName]
            vectorLayer = QgsMapLayerRegistry.instance().mapLayer(id)
            searchString = "ID IN ('{}')".format("','".join(ids))

            error = ""
            fIds = self.__search(vectorLayer, searchString, error)
            if error != "":
                qWarning(error)
                return
            else:
                vectorLayer.setSelectedFeatures(fIds)

    def __search(self, layer, searchString, error):
        """

        :param layer: QgsVectorLayer
        :param searchString: str
        :param error: str
        :return:
        """
        search = QgsExpression(searchString)
        rect = QgsRectangle()
        fIds = []

        if search.hasParserError():
            error += "Parsing error:" + search.parserErrorString()
            return fIds
        if search.prepare(layer.pendingFields()) is False:
            error + "Evaluation error:" + search.evalErrorString()

        layer.select(rect, False)
        fit = QgsFeatureIterator(layer.getFeatures())
        f = QgsFeature()

        while fit.nextFeature(f):
            if int(search.evaluate(f)) != 0:
                fIds.append(f.id())
            if search.hasEvalError():
                break

        return fIds

    def loadVfkButton_clicked(self):
        fileName = self.vfkFileLineEdit.text()

        if self.__mLastVfkFile != fileName:
            errorMsg = ""
            fInfo = QFileInfo(fileName)
            self.__mDataSourceName = QDir(fInfo.absolutePath()).filePath(fInfo.baseName() + '.db')

            if self.loadVfkFile(fileName, errorMsg) is False:
                msg2 = u'Nepodařilo se získat OGR provider'
                QMessageBox.critical(self, u'Nepodařilo se získat data provider', msg2)
                self.enableSearch.emit(False)
                return

            if self.__openDatabase(self.__mDataSourceName) is False:
                msg1 = u'Nepodařilo se otevřít databázi.'
                if QSqlDatabase.isDriverAvailable('QSQLITE') is False:
                    msg1 += u'\nDatabázový ovladač QSQLITE není dostupný.'
                QMessageBox.critical(self, u'Chyba', msg1)
                self.enableSearch.emit(False)
                return

            self.vfkBrowser.setConnectionName(str(self.property("connectionName")))
            self.__mSearchController.setConnectionName(str(self.property("connectionName")))

            self.enableSearch.emit(True)
            self.__mLastVfkFile = fileName
            self.__mLoadedLayers.clear()

        if self.parCheckBox.isChecked():
            self.__loadVfkLayer('PAR')
        else:
            self.__unLoadVfkLayer('PAR')

        if self.budCheckBox.isChecked():
            self.__loadVfkLayer('BUD')
        else:
            self.__unLoadVfkLayer('BUD')

    def vfkFileLineEdit_textChanged(self, arg1):
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
        qWarning("Loading vfk layer {}".format(vfkLayerName))
        if vfkLayerName in self.__mLoadedLayers:
            qWarning("Vfk layer {} is already loaded".format(vfkLayerName))
            return

        composedURI = self.__mLastVfkFile + "|layername=" + vfkLayerName
        layer = QgsVectorLayer(composedURI, vfkLayerName, "ogr")
        if not layer.isValid():
            qWarning("Layer failed to load!")

        self.__mLoadedLayers[vfkLayerName] = layer.id()
        self.__setSymbology(layer)

        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def __unLoadVfkLayer(self, vfkLayerName):
        qWarning("Unloading vfk layer {}".format(vfkLayerName))

        if vfkLayerName not in self.__mLoadedLayers:
            qWarning("Vfk layer {} is already unloaded".format(vfkLayerName))
            return

        QgsMapLayerRegistry.instance().removeMapLayer(self.__mLoadedLayers[vfkLayerName])
        del self.__mLoadedLayers[vfkLayerName]

    def __setSymbology(self, layer):
        name = layer.name()
        symbologyFile = ""

        if name == 'PAR':
            symbologyFile = ':/parStyle.qml'
        elif name == 'BUD':
            symbologyFile = ':/budStyle.qml'

        resultFlag = True
        errorMsg = layer.loadNamedStyle(symbologyFile, resultFlag)
        if resultFlag is False:
            QMessageBox.information(self, 'Load Style', errorMsg)

        layer.triggerRepaint()
        self.refreshLegend.emit(layer)

        return True

    def __openDatabase(self, dbPath):
        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        qWarning(dbPath)
        db.setDatabaseName(dbPath)
        if db.open() is False:
            return False
        else:
            self.setProperty("connectionName", connectionName)
            return True

    def loadVfkFile(self, fileName, errorMsg):

        if self.__mOgrDataSource is not None:
            self.__mOgrDataSource.Destroy()
            self.__mOgrDataSource = 0

        QgsApplication.registerOgrDrivers()

        progress = QProgressDialog(self)
        progress.setWindowTitle(u'Načítám VFK data...')
        progress.setLabelText(u'Načítám data do SQLite databáze (může nějaký čas trvat...)')
        progress.setRange(0, 1)
        progress.setModal(True)
        progress.show()

        QgsApplication.processEvents()
        progress.setValue(1)

        qWarning("Open OGR datasource (using DB: {})".format(self.__mDataSourceName))
        self.__mOgrDataSource = ogr.Open(self.__fileName, 0)
        if self.__mOgrDataSource is None:
            errorMsg = u'Unable to set open OGR data source'
            return False
        else:
            layerCount = self.__mOgrDataSource.GetLayerCount()
            progress.setRange(0, layerCount -1)

            if self.__mOgrDataSource.GetLayer().TestCapability('IsPreProcessed') is False:
                extraMsg = u'Načítám data do SQLite databáze (může nějaký čas trvat...)'

            for i in xrange(layerCount):
                if progress.wasCanceled():
                    errorMsg = u'Opening database stopped'
                    return False

                progress.setValue(i)

                theLayerName = self.__mOgrDataSource.GetLayer(i).GetLayerDefn().GetName()

                progress.setLabelText(u"VFK data {}/{}: {}\n{}".format(i, layerCount, theLayerName, extraMsg))
                self.__mOgrDataSource.GetLayer(i).GetFeatureCount(1)

            progress.hide()

            return True

    def __selectedIds(self, layer):
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
                qWarning("Vrstva {} obsazena..".format(layer))
                id = str(self.__mLoadedLayers[layer])
                vectorLayer = QgsMapLayerRegistry.instance().mapLayer(id)
                layerIds[layer] = self.__selectedIds(vectorLayer)

        self.vfkBrowser.showInfoAboutSelection(layerIds["PAR"], layerIds["BUD"])

    def showParInMap(self, ids):
        if self.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "PAR")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "PAR")

    def showBudInMap(self, ids):
        if self.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "BUD")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "BUD")

    def showOnCuzk(self):
        x = self.vfkBrowser.currentDefinitionPoint().first.split(".")[0]
        y= self.vfkBrowser.currentDefinitionPoint().second.split(".")[0]

        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(y, x)
        QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))

    @pyqtSlot()
    def switchToImport(self):
        self.actionImport.trigger()

    @pyqtSlot(int)
    def switchToSearch(self, searchType):
        """
        :param searchType: int
        """
        self.actionVyhledavani.trigger()
        self.searchCombo.setCurrentIndex(searchType)
        self.searchForms.setCurrentIndex(searchType)

    def __createToolbarsAndConnect(self):

        # Main toolbar
        # ------------
        # self.__mainToolBar = QToolBar(self)
        # self.__mainToolBar.addAction(self.ui.actionImport)
        # self.__mainToolBar.addAction(self.ui.actionVyhledavani)
        # self.__mainToolBar.setOrientation(Qt.Vertical)
        # self.addToolBar(Qt.LeftToolBarArea, self.__mainToolBar)

        actionGroup = QActionGroup(self)
        actionGroup.addAction(self.actionImport)
        actionGroup.addAction(self.actionVyhledavani)

        # QSignalMapper
        # -------------
        self.signalMapper = QSignalMapper(self)

        # connect to 'clicked' on all buttons
        self.connect(self.actionImport, SIGNAL("triggered()"), self.signalMapper, SLOT("map()"))
        self.connect(self.actionVyhledavani, SIGNAL("triggered()"), self.signalMapper, SLOT("map()"))

        # setMapping on each button to the QStackedWidget index we'd like to switch to
        self.signalMapper.setMapping(self.actionImport, 0)
        self.signalMapper.setMapping(self.actionVyhledavani, 1)

        # connect mapper to stackedWidget
        self.connect(self.signalMapper, SIGNAL("mapped(int)"), self.stackedWidget, SLOT("setCurrentIndex(int)"))
        self.actionImport.trigger()

        self.connect(self.vfkBrowser, SIGNAL("switchToPanelImport()"), self.switchToImport)
        self.connect(self.vfkBrowser, SIGNAL("switchToPanelSearch(int)"), self, SLOT("switchToSearch(int)"))

        # Browser toolbar
        # ---------------
        self.__mBrowserToolbar = QToolBar(self)
        self.connect(self.actionBack, SIGNAL("triggered()"), self.vfkBrowser.goBack)
        self.connect(self.actionForward, SIGNAL("triggered()"), self.vfkBrowser.goForth)
        self.actionSelectBudInMap.triggered.connect(self.selectBudInMap)
        self.actionSelectParInMap.triggered.connect(self.selectParInMap)
        self.actionCuzkPage.triggered.connect(self.showOnCuzk)
        self.actionExportLatex.triggered.connect(self.latexExport)
        self.actionExportHtml.triggered.connect(self.htmlExport)
        self.connect(self.actionShowInfoaboutSelection, SIGNAL("toggled(bool)"), self,
                     SLOT("setSelectionChangedConnected(bool)"))
        self.connect(self.actionShowHelpPage, SIGNAL("triggered()"), self.vfkBrowser.showHelpPage)

        self.browseButton.clicked.connect(self.browseButton_clicked)
        self.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

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
        self.connect(self.vfkBrowser, SIGNAL("currentParIdsChanged(bool)"),
                     self.actionSelectParInMap, SLOT("setEnabled(bool)"))
        self.connect(self.vfkBrowser, SIGNAL("currentBudIdsChanged(bool)"),
                     self.actionSelectBudInMap, SLOT("setEnabled(bool)"))
        self.connect(self.vfkBrowser, SIGNAL("historyBefore(bool)"), self.actionBack, SLOT("setEnabled(bool)"))
        self.connect(self.vfkBrowser, SIGNAL("historyAfter(bool)"), self.actionForward, SLOT("setEnabled(bool)"))
        self.connect(self.vfkBrowser, SIGNAL("definitionPointAvailable(bool)"),
                     self.actionCuzkPage, SLOT("setEnabled(bool)"))
