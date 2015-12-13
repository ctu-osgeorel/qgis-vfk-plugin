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
import htmlDocument
import domains
from vfkTextBrowser import *
from searchFormController import *
from budovySearchForm import *
from jednotkySearchForm import *
from parcelySearchForm import *


class MainApp (QtGui.QMainWindow):
    # signals
    goBack = pyqtSignal()
    searchOpsubByName = pyqtSignal(str)
    enableSearch = pyqtSignal(bool)
    refreshLegend = pyqtSignal(QgsMapLayer)

    class VfkLayer(object):
        Par = 0
        Bud = 1

    def __init__(self, iface, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.iface = iface

        # Set up the user interface from Designer.
        self.ui = Ui_MainApp()
        self.ui.setupUi(self)

        # variables
        self.__mLastVfkFile = ""
        self.__mOgrDataSource = None
        self.__mDataSourceName = ""
        self.__fileName = ""
        self.__mLoadedLayers = {}

        # settings of custom widgets
        self.ui.vfkBrowser = VfkTextBrowser()
        self.ui.parcelySearchForm = ParcelySearchForm()
        self.ui.vlastniciSearchForm = VlastniciSearchForm()
        self.ui.budovySearchForm = BudovySearchForm()
        self.ui.jednotkySearchForm = JednotkySearchForm()

        # Connect ui with functions
        self.__createToolbarsAndConnect()

        # settings
        self.ui.loadVfkButton.setDisabled(True)
        self.__mDefaultPalette = self.ui.vfkFileLineEdit.palette()

        self.searchFormMainControls = SearchFormController.MainControls
        self.searchFormMainControls.formCombobox = self.ui.searchCombo
        self.searchFormMainControls.searchForms = self.ui.searchForms
        self.searchFormMainControls.searchButton = self.ui.searchButton

        self.searchForms = SearchFormController.SearchForms
        self.searchForms.vlastnici = self.ui.vlastniciSearchForm
        self.searchForms.parcely = self.ui.parcelySearchForm
        self.searchForms.budovy = self.ui.budovySearchForm
        self.searchForms.jednotky = self.ui.jednotkySearchForm

        # search form controller
        self.__mSearchController = SearchFormController(self.searchFormMainControls, self.searchForms, self)

        self.connect(self.__mSearchController, SIGNAL("actionTriggered(QUrl)"), self.ui.vfkBrowser.processAction)
        self.connect(self, SIGNAL("enableSearch(bool)"), self.ui.searchButton.setEnabled)
        self.connect(self.ui.vfkBrowser, SIGNAL("showParcely(QObject)"), self.showParInMap)
        self.connect(self.ui.vfkBrowser, SIGNAL("showBudovy(QObject)"), self.showBudInMap)

        self.ui.vfkBrowser.showHelpPage()

    @pyqtSlot()
    def browseButton_clicked(self):
        title = u'Načti soubor VFK'
        lastUsedDir = ''
        self.__fileName = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Soubor VFK (*.vfk)')
        if self.__fileName == "":
            return
        else:
            self.ui.vfkFileLineEdit.setText(self.__fileName)
            self.ui.loadVfkButton.setEnabled(True)

    @pyqtSlot()
    def browserGoBack(self):
        self.ui.vfkBrowser.goBack()

    @pyqtSlot()
    def browserGoForward(self):
        self.ui.vfkBrowser.goForth()

    @pyqtSlot()
    def selectParInMap(self):
        self.showInMap(self.ui.vfkBrowser.currentParIds(), "PAR")

    @pyqtSlot()
    def selectBudInMap(self):
        self.showInMap(self.ui.vfkBrowser.currentBudIds(), "BUD")

    @pyqtSlot()
    def latexExport(self):
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", "", "LaTeX (*.tex)")
        if fileName is not None:
            VfkTextBrowser.exportDocument(VfkTextBrowser.currentUrl(), fileName, VfkTextBrowser.Latex)

    @pyqtSlot()
    def htmlExport(self):
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", "", "HTML (*.html)")
        if fileName is not None:
            VfkTextBrowser.exportDocument(VfkTextBrowser.currentUrl(), fileName, VfkTextBrowser.Html)

    @pyqtSlot(bool)
    def setSelectionChangedConnected(self, connected):
        for i, id in enumerate(self.__mLoadedLayers):
            vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))

            qWarning(".... setSelectionChangedConnected...........")

            if connected is True:
                self.connect(vectorLayer, SIGNAL("selectionChanged()"), self, SLOT("showInfoAboutSelection()"))
            else:
                self.disconnect(vectorLayer, SIGNAL("selectionChanged()"), self, SLOT("showInfoAboutSelection()"))

    @pyqtSlot(list, str)
    def showInMap(self, ids, layerName):
        if self.__mLoadedLayers.has_key(layerName):
            id = self.__mLoadedLayers[layerName]
            vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))
            searchString = "ID IN ('{}')".format(ids.join("','"))

            error = ""
            fIds = self.__search(vectorLayer, searchString, error)
            if error != "":
                qWarning(error)
                return
            else:
                vectorLayer.setSelectedFeatures(fIds)

    def __search(self, layer, searchString, error):
        layer = QgsVectorLayer(layer)
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

    @pyqtSlot()
    def loadVfkButton_clicked(self):
        fileName = self.ui.vfkFileLineEdit.text()

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

            #self.ui.vfkBrowser.setConnectionName(str(self.property("connectionName")))

            #self.__mSearchController.setConnectionName( property( "connectionName" ).toString() );
            self.enableSearch.emit(True)
            self.__mLastVfkFile = fileName
            self.__mLoadedLayers.clear()

        if self.ui.parCheckBox.isChecked():
            self.__loadVfkLayer('PAR')
        else:
            self.__unLoadVfkLayer('PAR')

        if self.ui.budCheckBox.isChecked():
            self.__loadVfkLayer('BUD')
        else:
            self.__unLoadVfkLayer('BUD')

    @pyqtSlot()
    def vfkFileLineEdit_textChanged(self, arg1):
        info = QFileInfo(arg1)

        if info.isFile():
            self.ui.loadVfkButton.setEnabled(True)
            self.ui.vfkFileLineEdit.setPalette(self.__mDefaultPalette)
        else:
            self.ui.loadVfkButton.setEnabled(False)
            pal = QPalette(self.ui.vfkFileLineEdit.palette())
            pal.setColor(QPalette.text(), Qt.red)
            self.ui.vfkFileLineEdit.setPalette(pal)

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

    @pyqtSlot()
    def showInfoAboutSelection(self):
        layers = ["PAR", "BUD"]
        layerIds = {}

        for layer in layers:
            if layer in self.__mLoadedLayers:
                id = str(self.__mLoadedLayers[layer])
                vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))
                layerIds[layer] = self.__selectedIds(vectorLayer)

        VfkTextBrowser.showInfoAboutSelection(layerIds["PAR"], layerIds["BUD"])

    @pyqtSlot()
    def showParInMap(self, ids):
        if self.ui.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "PAR")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "PAR")

    @pyqtSlot()
    def showBudInMap(self, ids):
        if self.ui.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "BUD")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "BUD")

    @pyqtSlot()
    def showOnCuzk(self):
        #x = .currentDefinitionPoint.definitionPoint.x
        #y = self.textBrowser.currentDefinitionPoint.definitionPoint.x
        x = 1136942
        y = 671128
        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(y, x)
        QDesktopServices.openUrl(QUrl(url))

    @pyqtSlot()
    def switchToImport(self):
        self.ui.actionImport.trigger()

    @pyqtSlot(int)
    def switchToSearch(self, searchType):
        """
        :param searchType: int
        """
        self.ui.actionVyhledavani.trigger()
        self.ui.searchCombo.setCurrentIndex(searchType)
        self.ui.searchForms.setCurrentIndex(searchType)

    def __createToolbarsAndConnect(self):

        # Main toolbar
        # ------------
        __mainToolBar = QToolBar(self)
        __mainToolBar.addAction(self.ui.actionImport)
        __mainToolBar.addAction(self.ui.actionVyhledavani)
        __mainToolBar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, __mainToolBar)

        actionGroup = QActionGroup(self)
        actionGroup.addAction(self.ui.actionImport)
        actionGroup.addAction(self.ui.actionVyhledavani)

        # QSignalMapper
        # -------------
        self.ui.signalMapper = QSignalMapper(self)

        # connect to 'clicked' on all buttons
        self.connect(self.ui.actionVyhledavani, SIGNAL("triggered()"), self.ui.signalMapper, SLOT("map()"))
        self.connect(self.ui.actionImport, SIGNAL("triggered()"), self.ui.signalMapper, SLOT("map()"))

        # setMapping on each button to the QStackedWidget index we'd like to switch to
        self.ui.signalMapper.setMapping(self.ui.actionImport, 0)
        self.ui.signalMapper.setMapping(self.ui.actionVyhledavani, 1)

        # connect mapper to stackedWidget
        self.connect(self.ui.signalMapper, SIGNAL("mapped(int)"), self.ui.stackedWidget, SLOT("setCurrentIndex(int)"))
        self.ui.actionImport.trigger()

        self.connect(self.ui.vfkBrowser, SIGNAL("switchToPanelImport()"), self.switchToImport)
        self.connect(self.ui.vfkBrowser, SIGNAL("switchToPanelSearch(int)"), SLOT("switchToSearch(int)"))

        # Browser toolbar
        # ---------------
        __mBrowserToolbar = QToolBar(self)
        self.connect(self.ui.actionBack, SIGNAL("triggered()"), self.ui.vfkBrowser.goBack)
        self.connect(self.ui.actionForward, SIGNAL("triggered()"), self.ui.vfkBrowser.goForth)
        self.ui.actionSelectBudInMap.triggered.connect(self.selectBudInMap)
        self.ui.actionSelectParInMap.triggered.connect(self.selectParInMap)
        self.ui.actionCuzkPage.triggered.connect(self.showOnCuzk)
        self.ui.actionExportLatex.triggered.connect(self.latexExport)
        self.ui.actionExportHtml.triggered.connect(self.htmlExport)
        self.connect(self.ui.actionShowInfoaboutSelection, SIGNAL("toggled(bool)"),
                     self.setSelectionChangedConnected)
        self.connect(self.ui.actionShowHelpPage, SIGNAL("triggered()"), self.ui.vfkBrowser.showHelpPage)

        self.ui.browseButton.clicked.connect(self.browseButton_clicked)
        self.ui.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

        bt = QToolButton(__mBrowserToolbar)
        bt.setPopupMode(QToolButton.InstantPopup)
        bt.setText("Export ")

        menu = QMenu(bt)
        menu.addAction(self.ui.actionExportLatex)
        menu.addAction(self.ui.actionExportHtml)
        bt.setMenu(menu)

        __mBrowserToolbar.addAction(self.ui.actionBack)
        __mBrowserToolbar.addAction(self.ui.actionForward)
        __mBrowserToolbar.addAction(self.ui.actionSelectParInMap)
        __mBrowserToolbar.addAction(self.ui.actionSelectBudInMap)
        __mBrowserToolbar.addAction(self.ui.actionCuzkPage)
        __mBrowserToolbar.addSeparator()
        __mBrowserToolbar.addAction(self.ui.actionShowInfoaboutSelection)
        __mBrowserToolbar.addSeparator()
        __mBrowserToolbar.addWidget(bt)
        __mBrowserToolbar.addSeparator()
        __mBrowserToolbar.addAction(self.ui.actionShowHelpPage)

        self.ui.rightWidgetLayout.insertWidget(0, __mBrowserToolbar)
