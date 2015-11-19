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
from PyQt4.QtCore import QUuid, QFileInfo, QDir, QObject, QSignalMapper, SIGNAL, SLOT
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *
from qgis.gui import *
from ui_MainApp import Ui_MainApp
import ogr, gdal

import htmlDocument
import domains
from vfkTextBrowser import *


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
        self.mSearchController = None

        # Connect ui with functions
        self.createToolbarsAndConnect()

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
        pass
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

    def showInMap(self, ids, layerName):
        if self.mLoadedLayers.has_key(layerName):
            id = self.mLoadedLayers[layerName]
            vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))
            searchString = "ID IN ('{}')".format(ids.join("','"))

            error = ""
            fIds = self.search(vectorLayer, searchString, error)
            if error != "":
                print(error)
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
                # emit enableSearch( false )
                return

            if self.openDatabase(self.mDataSourceName) is False:
                msg1 = u'Nepodařilo se otevřít databázi.'
                if QSqlDatabase.isDriverAvailable('QSQLITE') is False:
                    msg1 += u'\nDatabázový ovladač QSQLITE není dostupný.'
                QMessageBox.critical(self, u'Chyba', msg1)

                # emit enableSearch( false )
                return

            #self.ui.vfkBrowser.setConnectionName(str(self.property("connectionName")))

            #self.mSearchController.setConnectionName( property( "connectionName" ).toString() );
            # emit enableSearch( true );

        if self.ui.parCheckBox.isChecked():
            self.loadVfkLayer('PAR')
        else:
            self.unLoadVfkLayer('PAR')

        if self.ui.budCheckBox.isChecked():
            self.loadVfkLayer('BUD')
        else:
            self.unLoadVfkLayer('BUD')

    # for debug
    def printMsg(self, msg):
        QMessageBox.information(self.iface.mainWindow(), "Debug", msg)

    def loadVfkLayer(self, vfkLayerName):
        if vfkLayerName in self.mLoadedLayers:
            print("Vfk layer {} is already loaded".format(vfkLayerName))
            return

        uri = self.fileName
        #composedURI = self.fileName
        layer = QgsVectorLayer(uri, vfkLayerName, 'ogr')
        if not layer.isValid():
            print "Layer failed to load!"

        self.mLoadedLayers[vfkLayerName] = layer.id()
        self.setSymbology(layer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def unLoadVfkLayer(self, vfkLayerName):
        if vfkLayerName in self.mLoadedLayers:
            QgsMapLayerRegistry.instance().removeMapLayer(self.mLoadedLayers[vfkLayerName].id())
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

        # emit refreshLegend( layer )

        return True

    def openDatabase(self, dbPath):
        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        db.setDatabaseName(dbPath)
        if db.open() is False:
            return False
        else:
            self.setProperty("connectionName", connectionName)
            return True

    def loadVfkFile(self, fileName, errorMsg):

        if self.mOgrDataSource is not None:
            self.mOgrDataSource.Destroy()
            self.mOgrDataSource = None

        QgsApplication.registerOgrDrivers()

        progress = QProgressDialog(self)
        progress.setWindowTitle(u'Načítám VFK data...')
        progress.setLabelText(u'Načítám data do SQLite databáze (může nějaký čas trvat...)')
        progress.setRange(0, 1)
        progress.setModal(True)
        progress.show()

        progress.setValue(1)

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
            if self.mLoadedLayers.has_key(layer):
                id = str(self.mLoadedLayers[layer])
                vectorLayer = QgsVectorLayer(QgsMapLayerRegistry.instance().mapLayer(id))
                layerIds[layer] = self.selectedIds(vectorLayer)
        self.ui.vfkBrowser.showInfoAboutSelection(layerIds["PAR"], layerIds["BUD"])

    def showOnCuzk(self):
        #x = .currentDefinitionPoint.definitionPoint.x
        #y = self.textBrowser.currentDefinitionPoint.definitionPoint.x
        x = 1136942.185
        y = 671128.312
        url = "http://nahlizenidokn.cuzk.cz/MapaIdentifikace.aspx?&x=-{}&y=-{}".format(y, x)
        QDesktopServices.openUrl(QUrl(url))

    def createToolbarsAndConnect(self):
        self.ui.browseButton.clicked.connect(self.browseButton_clicked)
        self.ui.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

        self.ui.actionCuzkPage.triggered.connect(self.showOnCuzk)
        self.ui.actionSelectBudInMap.triggered.connect(self.selectBudInMap)
        self.ui.actionSelectParInMap.triggered.connect(self.selectParInMap)
        self.ui.actionExportLatex.triggered.connect(self.latexExport)
        self.ui.actionExportHtml.triggered.connect(self.htmlExport)
        self.ui.actionShowInfoaboutSelection.toggled.connect(self.showInfoAboutSelection)

        self.ui.loadVfkButton.setEnabled(False)
