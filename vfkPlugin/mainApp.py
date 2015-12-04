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
import this
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QFileDialog, QMessageBox, QProgressDialog, QToolBar, QActionGroup
from PyQt4.QtCore import QUuid, QFileInfo, QDir, QObject, QSignalMapper, SIGNAL, SLOT, pyqtSignal
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
    def __init__(self, iface, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.iface = iface

        # Set up the user interface from Designer.
        self.ui = Ui_MainApp()
        self.ui.setupUi(self)

        # variables
        self.mLastVfkFile = ""
        self.mOgrDataSource = None
        self.mDataSourceName = ""
        self.fileName = ""
        self.mLoadedLayers = {}

        # Connect ui with functions
        self.createToolbarsAndConnect()

        # settings
        self.ui.loadVfkButton.setDisabled(True)
        self.mDefaultPalette = self.ui.vfkFileLineEdit.palette()

        self.searchFormMainControls = SearchFormController.MainControls
        self.searchFormMainControls.formCombobox = self.ui.searchCombo
        self.searchFormMainControls.searchForms = self.ui.searchForms
        self.searchFormMainControls.searchButton = self.ui.searchButton

        self.searchForms = SearchFormController.SearchForms
        self.searchForms.vlastnici = self.ui.vlastniciSearchForm
        self.searchForms.parcely = self.ui.parcelySearchForm
        self.searchForms.budovy = self.ui.budovySearchForm
        self.searchForms.jednotky = self.ui.jednotkySearchForm

        self.mSearchController = SearchFormController(self.searchFormMainControls, self.searchForms, self)

        self.connect(self.mSearchController, SIGNAL("actionTriggered(QUrl)"), self.ui.vfkBrowser, SLOT("processAction(QUrl)"))
        self.connect(self, SIGNAL("enableSearch(bool)"), self.ui.searchButton, SLOT("setEnabled(bool)"))

    # signals
    @staticmethod
    def goBack(): pass
    @staticmethod
    def searchOpsubByName(string): pass
    @staticmethod
    def enableSearch(enable): pass
    @staticmethod
    def refreshLegend(layer): pass

    def browseButton_clicked(self):
        title = u'Načti soubor VFK'
        lastUsedDir = ''
        self.fileName = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Soubor VFK (*.vfk)')
        if self.fileName == "":
            return
        else:
            self.ui.vfkFileLineEdit.setText(self.fileName)
            self.ui.loadVfkButton.setEnabled(True)

    def browserGoBack(self):
        self.ui.vfkBrowser.goBack()

    def browserGoForward(self):
        self.ui.vfkBrowser.goForth()

    def selectParInMap(self):
        pass

    def selectBudInMap(self):
        pass

    def latexExport(self):
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", "", "LaTeX (*.tex)")
        if fileName is None:
            self.ui.vfkBrowser.exportDocument(self.ui.vfkBrowser.currentUrl(), fileName, vfkTextBrowser.Latex)
            pass

    def htmlExport(self):
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", "", "HTML (*.html)")
        if fileName is None:
            self.ui.vfkBrowser.exportDocument(self.ui.vfkBrowser.currentUrl(), fileName, vfkTextBrowser.Html)
            pass

    def setSelectionChangedConnected(self, connected):
        for i, id in enumerate(self.mLoadedLayers):
            vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(i))

            if connected is True:
                self.connect(vectorLayer, SIGNAL("selectionChanged()"), self, SLOT("self.showInfoAboutSelection()"))
            else:
                self.disconnect(vectorLayer, SIGNAL("selectionChanged()"), self, SLOT("self.showInfoAboutSelection()"))

    def showInMap(self, ids, layerName):
        if self.mLoadedLayers.has_key(layerName):
            id = self.mLoadedLayers[layerName]
            vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))
            searchString = "ID IN ('{}')".format(ids.join("','"))

            error = ""
            fIds = self.search(vectorLayer, searchString, error)
            if error != "":
                QgsLogger.debug(error)
                return
            else:
                vectorLayer.setSelectedFeatures(fIds)

    def search(self, layer, searchString, error):
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

    def loadVfkButton_clicked(self):
        fileName = self.ui.vfkFileLineEdit.text()

        if self.mLastVfkFile != fileName:
            errorMsg = ""
            fInfo = QFileInfo(fileName)
            self.mDataSourceName = QDir(fInfo.absolutePath()).filePath(fInfo.baseName() + '.db')

            if self.loadVfkFile(fileName, errorMsg) is False:
                msg2 = u'Nepodařilo se získat OGR provider'
                QMessageBox.critical(self, u'Nepodařilo se získat data provider', msg2)
                return

            if self.openDatabase(self.mDataSourceName) is False:
                msg1 = u'Nepodařilo se otevřít databázi.'
                if QSqlDatabase.isDriverAvailable('QSQLITE') is False:
                    msg1 += u'\nDatabázový ovladač QSQLITE není dostupný.'
                QMessageBox.critical(self, u'Chyba', msg1)
                self.ui.loadVfkButton.emit(self.enableSearch(False))
                return

            #self.ui.vfkBrowser.setConnectionName(str(self.property("connectionName")))

            #self.mSearchController.setConnectionName( property( "connectionName" ).toString() );
            self.mLastVfkFile = fileName
            self.mLoadedLayers.clear()

        if self.ui.parCheckBox.isChecked():
            self.loadVfkLayer('PAR')
        else:
            self.unLoadVfkLayer('PAR')

        if self.ui.budCheckBox.isChecked():
            self.loadVfkLayer('BUD')
        else:
            self.unLoadVfkLayer('BUD')

    def vfkFileLineEdit_textChanged(self, arg1):
        info = QFileInfo(arg1)

        if info.isFile():
            self.ui.loadVfkButton.setEnabled(True)
            self.ui.vfkFileLineEdit.setPalette(self.mDefaultPalette)
        else:
            self.ui.loadVfkButton.setEnabled(False)
            pal = QPalette(self.ui.vfkFileLineEdit.palette())
            pal.setColor(QPalette.text(), QtCore.Qt.red)
            self.ui.vfkFileLineEdit.setPalette(pal)

    def loadVfkLayer(self, vfkLayerName):
        QgsLogger.debug("Loading vfk layer {}".format(vfkLayerName))
        if vfkLayerName in self.mLoadedLayers:
            QgsLogger.debug("Vfk layer {} is already loaded".format(vfkLayerName))
            return

        composedURI = self.mLastVfkFile + "|layername=" + vfkLayerName
        layer = QgsVectorLayer(composedURI, vfkLayerName, "ogr")
        if not layer.isValid():
            QgsLogger.debug("Layer failed to load!")

        self.mLoadedLayers[vfkLayerName] = layer.id()
        self.setSymbology(layer)

        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def unLoadVfkLayer(self, vfkLayerName):
        QgsLogger.debug("Unloading vfk layer {}".format(vfkLayerName))

        if vfkLayerName not in self.mLoadedLayers:
            QgsLogger.debug("Vfk layer {} is already unloaded".format(vfkLayerName))
            return

        QgsMapLayerRegistry.instance().removeMapLayer(self.mLoadedLayers[vfkLayerName])
        del self.mLoadedLayers[vfkLayerName]

    def setSymbology(self, layer):
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
        self.refreshLegend(layer) #############################

        return True

    def openDatabase(self, dbPath):
        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        QgsLogger.debug(dbPath)
        db.setDatabaseName(dbPath)
        if db.open() is False:
            return False
        else:
            self.setProperty("connectionName", connectionName)
            return True

    def loadVfkFile(self, fileName, errorMsg):

        if self.mOgrDataSource is not None:
            self.mOgrDataSource.Destroy()
            self.mOgrDataSource = 0

        QgsApplication.registerOgrDrivers()

        progress = QProgressDialog(self)
        progress.setWindowTitle(u'Načítám VFK data...')
        progress.setLabelText(u'Načítám data do SQLite databáze (může nějaký čas trvat...)')
        progress.setRange(0, 1)
        progress.setModal(True)
        progress.show()

        progress.setValue(1)

        QgsLogger.debug("Open OGR datasource (using DB: {})".format(self.mDataSourceName))
        self.mOgrDataSource = ogr.Open(self.fileName, 0)
        if self.mOgrDataSource is None:
            errorMsg = u'Unable to set open OGR data source'
            return False
        else:
            layerCount = self.mOgrDataSource.GetLayerCount()
            progress.setRange(0, layerCount -1)

            if self.mOgrDataSource.GetLayer().TestCapability('IsPreProcessed') is False:
                extraMsg = u'Načítám data do SQLite databáze (může nějaký čas trvat...)'

            for i in xrange(layerCount):
                if progress.wasCanceled():
                    errorMsg = u'Opening database stopped'
                    return False

                progress.setValue(i)

                theLayerName = self.mOgrDataSource.GetLayer(i).GetLayerDefn().GetName()

                progress.setLabelText(u"VFK data {}/{}: {}\n{}".format(i, layerCount, theLayerName, extraMsg))
                self.mOgrDataSource.GetLayer(i).GetFeatureCount(1)

            progress.hide()

            return True

    def selectedIds(self, layer):
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
            if layer in self.mLoadedLayers:
                id = str(self.mLoadedLayers[layer])
                vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))
                layerIds[layer] = self.selectedIds(vectorLayer)

        vfkTextBrowser.showInfoAboutSelection(layerIds["PAR"], layerIds["BUD"])

    def showParInMap(self, ids):
        if self.ui.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "PAR")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "PAR")

    def showBudInMap(self, ids):
        if self.ui.actionShowInfoaboutSelection.isChecked():
            self.setSelectionChangedConnected(False)
            self.showInMap(ids, "BUD")
            self.setSelectionChangedConnected(True)
        else:
            self.showInMap(ids, "BUD")



    def showOnCuzk(self):
        #x = .currentDefinitionPoint.definitionPoint.x
        #y = self.textBrowser.currentDefinitionPoint.definitionPoint.x
        x = 1136942
        y = 671128
        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(y, x)
        QDesktopServices.openUrl(QUrl(url))

    def switchToImport(self):
        self.ui.actionImport.trigger()

    def switchToSearch(self, searchType):
        self.ui.actionVyhledavani.trigger()
        self.ui.searchCombo.setCurrentIndex(searchType)
        self.ui.searchForms.setCurrentIndex(searchType)

    def createToolbarsAndConnect(self):

        # Main toolbar
        # ------------
        self.ui.mainToolBar = QToolBar(self)
        self.ui.mainToolBar.addAction(self.ui.actionImport)
        self.ui.mainToolBar.addAction(self.ui.actionVyhledavani)
        self.ui.mainToolBar.setOrientation(QtCore.Qt.Vertical)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.ui.mainToolBar)

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
        self.connect(self.ui.signalMapper, SIGNAL("mapped(int)"), self.ui.stackedWidget, SLOT("setCurrentIndex( int )"))
        self.ui.actionImport.trigger()

        self.connect(self.ui.vfkBrowser, SIGNAL("switchToPanelImport()"), self, SLOT("switchToImport()"))
        self.connect(self.ui.vfkBrowser, SIGNAL("switchToPanelSearch(int)"), self, SLOT("switchToSearch(int)"))

        # Browser toolbar
        # ---------------
        mBrowserToolbar = QToolBar(self)
        self.connect(self.ui.actionBack, SIGNAL("triggered()"), self.ui.vfkBrowser, SLOT("goBack()"))
        self.connect(self.ui.actionForward, SIGNAL("triggered()"), self.ui.vfkBrowser, SLOT("goForth()"))
        self.ui.actionSelectBudInMap.triggered.connect(self.selectBudInMap)
        self.ui.actionSelectParInMap.triggered.connect(self.selectParInMap)
        self.ui.actionCuzkPage.triggered.connect(self.showOnCuzk)
        self.ui.actionExportLatex.triggered.connect(self.latexExport)
        self.ui.actionExportHtml.triggered.connect(self.htmlExport)
        self.connect(self.ui.actionShowInfoaboutSelection, SIGNAL("toggled(bool)"), self, SLOT("setSelectionChangedConnected(bool)"))

        self.ui.browseButton.clicked.connect(self.browseButton_clicked)
        self.ui.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

        bt = QToolButton(mBrowserToolbar)
        bt.setPopupMode(QToolButton.InstantPopup)
        bt.setText("Export ")

        menu = QMenu(bt)
        menu.addAction(self.ui.actionExportLatex)
        menu.addAction(self.ui.actionExportHtml)
        bt.setMenu(menu)

        mBrowserToolbar.addAction(self.ui.actionBack)
        mBrowserToolbar.addAction(self.ui.actionForward)
        mBrowserToolbar.addAction(self.ui.actionSelectParInMap)
        mBrowserToolbar.addAction(self.ui.actionSelectBudInMap)
        mBrowserToolbar.addSeparator()
        mBrowserToolbar.addAction(self.ui.actionShowInfoaboutSelection)
        mBrowserToolbar.addSeparator()
        mBrowserToolbar.addWidget(bt)
        mBrowserToolbar.addSeparator()
        mBrowserToolbar.addAction(self.ui.actionShowHelpPage)

        self.ui.rightWidgetLayout.insertWidget(0, mBrowserToolbar)


        #self.ui.loadVfkButton.setEnabled(False)




