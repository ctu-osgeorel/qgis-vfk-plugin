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
from PyQt4.QtGui import QFileDialog, QMessageBox, QProgressDialog, QToolBar, QActionGroup, QDockWidget, QToolButton, QMenu, QPalette, QDesktopServices
from PyQt4.QtCore import QUuid, QFileInfo, QDir, Qt, QObject, QSignalMapper, SIGNAL, SLOT, pyqtSignal, qDebug, QThread
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *
from qgis.gui import *
import ogr

from ui_MainApp import Ui_MainApp
from searchFormController import *
from importThread import *
from openThread import *


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
        self.__mLastVfkFile = ''
        self.__mOgrDataSource = None
        self.__mDataSourceName = ''
        self.__fileName = ''
        self.__mLoadedLayers = {}
        self.__mDefaultPalette = self.vfkFileLineEdit.palette()

        # Connect ui with functions
        self.__createToolbarsAndConnect()

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
        self.__mSearchController = SearchFormController(self.searchFormMainControls, self.searchForms, self)

        self.connect(self.__mSearchController, SIGNAL("actionTriggered(QUrl)"), self.vfkBrowser.processAction)
        self.connect(self, SIGNAL("enableSearch"), self.searchButton.setEnabled)

        self.connect(self.vfkBrowser, SIGNAL("showParcely"), self.showParInMap)
        self.connect(self.vfkBrowser, SIGNAL("showBudovy"), self.showBudInMap)

        # connect lineEdits and returnPressed action
        self.connect(self.vfkFileLineEdit, SIGNAL("returnPressed()"), self.loadVfkButton_clicked)
        self.connect(self.vlastniciSearchForm.ui.jmenoLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.vlastniciSearchForm.ui.rcIcoLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.vlastniciSearchForm.ui.lvVlastniciLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.connect(self.parcelySearchForm.ui.parCisloLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.parcelySearchForm.ui.lvParcelyLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.connect(self.budovySearchForm.ui.cisloDomovniLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.budovySearchForm.ui.naParceleLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.budovySearchForm.ui.lvBudovyLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.connect(self.jednotkySearchForm.ui.mCisloJednotkyLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.jednotkySearchForm.ui.mCisloDomovniLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.jednotkySearchForm.ui.mNaParceleLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)
        self.connect(self.jednotkySearchForm.ui.mLvJednotkyLineEdit, SIGNAL("returnPressed()"), self.__mSearchController.search)

        self.vfkBrowser.showHelpPage()

    def browseButton_clicked(self):
        title = u'Načti soubor VFK'
        lastUsedDir = ''
        self.__fileName = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Soubor VFK (*.vfk)')
        if not self.__fileName:
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
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", ".tex", "LaTeX (*.tex)")
        if fileName:
            self.vfkBrowser.exportDocument(self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Latex)
            self.succesfullExport("LaTeX")

    def htmlExport(self):
        fileName = QFileDialog.getSaveFileName(self, u"Jméno exportovaného souboru", ".html", "HTML (*.html)")
        if fileName:
            self.vfkBrowser.exportDocument(self.vfkBrowser.currentUrl(), fileName, self.vfkBrowser.ExportFormat.Html)
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
                self.connect(vectorLayer, SIGNAL("selectionChanged()"), self.showInfoAboutSelection)
            else:
                self.disconnect(vectorLayer, SIGNAL("selectionChanged()"), self.showInfoAboutSelection)

    def showInMap(self, ids, layerName):
        """

        :type ids: list
        :type layerName: str
        :return:
        """
        if layerName in self.__mLoadedLayers:
            id = self.__mLoadedLayers[layerName]
            vectorLayer = QgsMapLayerRegistry.instance().mapLayer(id)
            searchString = "ID IN ('{}')".format("','".join(ids))
            qDebug(searchString)
            error = ''
            fIds = self.__search(vectorLayer, searchString, error)
            if error:
                qDebug(error)
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
            if search.evaluate(f) != 0:
                fIds.append(f.id())
            if search.hasEvalError():
                qDebug(error)
                break

        return fIds

    def loadVfkButton_clicked(self):
        fileName = self.vfkFileLineEdit.text()

        if self.__mLastVfkFile != fileName:
            errorMsg = ''
            fInfo = QFileInfo(fileName)
            self.__mDataSourceName = QDir(fInfo.absolutePath()).filePath(fInfo.baseName() + '.db')

            if not self.loadVfkFile(fileName, errorMsg):
                msg2 = u'Nepodařilo se získat OGR provider'
                QMessageBox.critical(self, u'Nepodařilo se získat data provider', msg2)
                self.emit(SIGNAL("enableSearch"), False)
                return

            if not self.__openDatabase(self.__mDataSourceName):
                msg1 = u'Nepodařilo se otevřít databázi.'
                if not QSqlDatabase.isDriverAvailable('QSQLITE'):
                    msg1 += u'\nDatabázový ovladač QSQLITE není dostupný.'
                QMessageBox.critical(self, u'Chyba', msg1)
                self.emit(SIGNAL("enableSearch"), False)
                return

            self.vfkBrowser.setConnectionName(self.property("connectionName"))
            self.__mSearchController.setConnectionName(self.property("connectionName"))

            self.emit(SIGNAL("enableSearch"), True)
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
        qDebug("Loading vfk layer {}".format(vfkLayerName))
        if vfkLayerName in self.__mLoadedLayers:
            qDebug("Vfk layer {} is already loaded".format(vfkLayerName))
            return

        composedURI = self.__mLastVfkFile + "|layername=" + vfkLayerName
        layer = QgsVectorLayer(composedURI, vfkLayerName, "ogr")
        if not layer.isValid():
            qDebug("Layer failed to load!")

        self.__mLoadedLayers[vfkLayerName] = layer.id()
        self.__setSymbology(layer)

        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def __unLoadVfkLayer(self, vfkLayerName):
        """

        :type vfkLayerName: str
        :return:
        """
        qDebug("Unloading vfk layer {}".format(vfkLayerName))

        if vfkLayerName not in self.__mLoadedLayers:
            qDebug("Vfk layer {} is already unloaded".format(vfkLayerName))
            return

        QgsMapLayerRegistry.instance().removeMapLayer(self.__mLoadedLayers[vfkLayerName])
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

        resultFlag = True
        errorMsg = layer.loadNamedStyle(symbologyFile, resultFlag)
        if resultFlag is False:
            QMessageBox.information(self, 'Load Style', errorMsg)

        layer.triggerRepaint()
        self.emit(SIGNAL("refreshLegend"), layer)

        return True

    def __openDatabase(self, dbPath):
        """

        :type dbPath: str
        :return:
        """
        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        qDebug(dbPath)
        db.setDatabaseName(dbPath)
        if db.open() is False:
            return False
        else:
            self.setProperty("connectionName", connectionName)
            return True

    def loadVfkFile(self, fileName, errorMsg):
        """

        :type fileName: str
        :type errorMsg: str
        :return:
        """

        if self.__mOgrDataSource:
            self.__mOgrDataSource.Destroy()
            self.__mOgrDataSource = 0

        QgsApplication.registerOgrDrivers()

        QgsApplication.processEvents()

        self.openThread = OpenThread()
        self.connect(self.openThread, SIGNAL("importStat()"), self.__openThreadStatus)

        qDebug("Opening OGR datasource (using DB: {})".format(self.__mDataSourceName))
        self.labelLoading.setText(u'Otevírám datasource {}...'.format(self.__fileName))
        if not self.openThread.isRunning():
            self.openThread.start()
            self.__mOgrDataSource = ogr.Open(self.__fileName, 0)

        layerCount = self.__mOgrDataSource.GetLayerCount()
        layers_names = []

        for i in xrange(layerCount):
            layers_names.append(self.__mOgrDataSource.GetLayer(i).GetLayerDefn().GetName())

        if 'PAR' not in layers_names or 'BUD' not in layers_names:
            self.__dataWithoutParBud()
            return True

        if not self.__mOgrDataSource:
            errorMsg = u'Nemohu otevřít datový zdroj OGR!'
            return False
        else:
            extraMsg = u''
            if not self.__mOgrDataSource.GetLayer().TestCapability('IsPreProcessed'):
                extraMsg = u'Načítám data do SQLite databáze (může nějaký čas trvat...)'

            self.progressBar.setRange(0, layerCount - 1)

            self.importThread = ImportThread(layers_names)
            self.connect(self.importThread, SIGNAL("importStatus(int, int)"), self.__importStatus)
            self.connect(self.importThread, SIGNAL("importFinished()"), self.__importFinished)

            if not self.importThread.isRunning():
                self.importThread.start()

            return True

    def __openThreadStatus(self):
        """

        :return:
        """

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

        self.vfkBrowser.showInfoAboutSelection(layerIds["PAR"], layerIds["BUD"])

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

        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(y, x)
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

    def succesfullExport(self, export_format):
        """

        :type export_format: str
        :return:
        """
        QMessageBox.information(self, u'Export', u"Export do formátu {} proběhl úspěšně.".format(export_format),
                                QMessageBox.Yes | QMessageBox.Yes)

    def __dataWithoutParBud(self):
        """

        :type export_format: str
        :return:
        """
        QMessageBox.warning(self, u'Upozornění', u"Zvolený VFK soubor neobsahuje vrstvy s geometrií (PAR, BUD), proto nemohou "
                                           u"být pomocí VFK Pluginu načtena. Data je možné načíst v QGIS pomocí volby "
                                           u"'Načíst vektorovou vrstvu.'", QMessageBox.Yes | QMessageBox.Yes)

    def __importFinished(self):
        """

        :return:
        """
        self.importThread.quit()
        QtGui.QMessageBox.information(self, u'Import', u"Import dat VFK proběhl úspěšně",QtGui.QMessageBox.Yes | QtGui.QMessageBox.Yes)
        self.progressBar.setValue(0)
        self.labelLoading.setText(u'Data úspěšně načtena.')

    def __importStatus(self, i, layerCount):
        """

        :return:
        """
        extraMsg = u'Načítám data do SQLite databáze (může nějaký čas trvat...)'
        theLayerName = self.__mOgrDataSource.GetLayer(i).GetLayerDefn().GetName()

        self.progressBar.setValue(self.progressBar.value() + 1)
        self.labelLoading.setText(u"VFK data {}/{}: {}\n{}".format(i+1, layerCount, theLayerName, extraMsg))
        self.__mOgrDataSource.GetLayer(i).GetFeatureCount(1)


    def __createToolbarsAndConnect(self):

        actionGroup = QActionGroup(self)
        actionGroup.addAction(self.actionImport)
        actionGroup.addAction(self.actionVyhledavani)

        # QSignalMapper
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

        self.connect(self.vfkBrowser, SIGNAL("switchToPanelImport"), self.switchToImport)
        self.connect(self.vfkBrowser, SIGNAL("switchToPanelSearch"), self.switchToSearch)

        # Browser toolbar
        # ---------------
        self.__mBrowserToolbar = QToolBar(self)
        self.connect(self.actionBack, SIGNAL("triggered()"), self.vfkBrowser.goBack)
        self.connect(self.actionForward, SIGNAL("triggered()"), self.vfkBrowser.goForth)

        self.connect(self.actionSelectBudInMap, SIGNAL("triggered()"), self.selectBudInMap)
        self.connect(self.actionSelectParInMap, SIGNAL("triggered()"), self.selectParInMap)
        self.connect(self.actionCuzkPage, SIGNAL("triggered()"), self.showOnCuzk)

        self.connect(self.actionExportLatex, SIGNAL("triggered()"), self.latexExport)
        self.connect(self.actionExportHtml, SIGNAL("triggered()"), self.htmlExport)

        self.connect(self.actionShowInfoaboutSelection, SIGNAL("toggled(bool)"), self.setSelectionChangedConnected)
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
        self.connect(self.vfkBrowser, SIGNAL("currentParIdsChanged"), self.actionSelectParInMap.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL("currentBudIdsChanged"), self.actionSelectBudInMap.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL("historyBefore"), self.actionBack.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL("historyAfter"), self.actionForward.setEnabled)
        self.connect(self.vfkBrowser, SIGNAL("definitionPointAvailable"), self.actionCuzkPage.setEnabled)
