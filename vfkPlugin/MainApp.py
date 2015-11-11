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
import os

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QFileDialog, QMessageBox, QProgressDialog, QToolBar, QActionGroup
from PyQt4.QtCore import QUuid, QFileInfo, QDir, QSignalMapper
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *
from qgis.gui import *
from ui_MainApp import Ui_MainApp
import ogr, gdal


class MainApp (QtGui.QMainWindow):

    mLastVfkFile = None
    mOgrDataSource = None # Check!!!
    mDataSourceName = None
    fileName = None
    mLoadedLayers = {}

    def __init__(self, iface, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.iface = iface

        # Set up the user interface from Designer.
        self.ui = Ui_MainApp()
        self.ui.setupUi(self)

        # Connect ui with functions
        self.createToolbarsAndConnect()

    def browseButton_clicked(self):
        title = u'Načti soubor VFK'
        lastUsedDir = ''
        self.fileName = QFileDialog.getOpenFileName(self, title, lastUsedDir, 'Soubor VFK (*.vfk)')
        if self.fileName is None:
            return
        else:
            self.ui.vfkFileLineEdit.setText(self.fileName)
            self.ui.loadVfkButton.setEnabled(True)

    def loadVfkButton_clicked(self):
        fileName = self.ui.vfkFileLineEdit.text()

        if self.mLastVfkFile != fileName:
            errorMsg = None
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
                QMessageBox.critical(self,u'Chyba', msg1)

                # emit enableSearch( false )
                return

            # vfkBrowser->setConnectionName( property( "connectionName" ).toString() );
            # mSearchController->setConnectionName( property( "connectionName" ).toString() );
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
    def printMsg(self,msg):
        QMessageBox.information(self.iface.mainWindow(),"Debug", msg)


    def loadVfkLayer( self, vfkLayerName):
        composedURI = self.fileName
        layer = QgsVectorLayer(composedURI, vfkLayerName, 'ogr')
        self.mLoadedLayers[vfkLayerName] = layer.id()
        self.setSymbology(layer)
        QgsMapLayerRegistry.instance().addMapLayer(layer, True)

    def unLoadVfkLayer(self, vfkLayerName):
        if vfkLayerName in self.mLoadedLayers:
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

        # emit refreshLegend( layer )

        return True


    def openDatabase(self, dbPath):
        connectionName = QUuid.createUuid().toString()
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        db.setDatabaseName(dbPath)
        if db.open() is False:
            return False
        else:
            #setProperty("connectionName", connectionName)
            return True


    def loadVfkFile(self, fileName, errorMsg):

        if self.mOgrDataSource:
            self.mOgrDataSource = 0

        progress = QProgressDialog(self)
        progress.setWindowTitle(u'Načítám VFK data...')
        progress.setLabelText(u'Načítám data do SQLite databáze (může nějaký čas trvat...)')
        progress.setRange(0, 1)
        progress.setModal(True)
        progress.show()

        self.mOgrDataSource = ogr.Open(self.fileName)
        if self.mOgrDataSource is False:
            errorMsg = u'Unable to set open OGR data source'
            return False

        layerCount = self.mOgrDataSource.GetLayerCount()
        progress.setRange(0, layerCount-1)

        if self.mOgrDataSource.TestCapability('IsPreProcessed') is False:
            extraMsg = u'Načítám data do SQLite databáze (může nějaký čas trvat...)'

        for i in xrange(layerCount):
            if progress.wasCanceled():
                errorMsg = u'Opening database stopped'
                return False
            progress.setValue(i)

        progress.hide()

        return True










    def createToolbarsAndConnect(self):
        self.ui.browseButton.clicked.connect(self.browseButton_clicked)
        self.ui.loadVfkButton.clicked.connect(self.loadVfkButton_clicked)

        self.ui.loadVfkButton.setEnabled(False)