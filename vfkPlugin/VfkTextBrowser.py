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

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import QFile, QIODevice, QUrl, QObject, SIGNAL, SLOT, pyqtSlot, pyqtSignal, QByteArray
from PyQt4.QtSql import QSqlDatabase
from collections import namedtuple

from vfkDocument import *
from documentBuilder import *


TaskList = namedtuple('TaskList', ['a', 'b'])


class HistoryRecord(object):
    def __init__(self):
        self.html = ""
        self.parIds = []
        self.budIds = []
        self.definitionPoint = Coordinates()


class VfkTextBrowser(QTextBrowser):

    class ExportFormat(object):
        Html = 0
        RichText = 1
        Latex = 2

    def __init__(self):
        super(VfkTextBrowser, self).__init__()

        self.__mCurrentUrl = QUrl()
        self.__mCurrentRecord = HistoryRecord()
        self.__mDocumentBuilder = DocumentBuilder()


    # signals
    updateHistory = pyqtSignal(HistoryRecord)
    showParcely = pyqtSignal(QObject)
    showBudovy = pyqtSignal(QObject)
    currentParIdsChanged = pyqtSignal(bool)
    currentBudIdsChanged = pyqtSignal(bool)
    historyBefore = pyqtSignal(bool)
    historyAfter = pyqtSignal(bool)
    definitionPointAvailable = pyqtSignal(bool)
    switchToPanelImport = pyqtSignal()
    switchToPanelSearch = pyqtSignal(int)

    def startPage(self):
        self.processAction(QUrl("showText?page=allTEL"))

    def documentFactory(self, format):
        format = self.ExportFormat()

        doc = VfkDocument()

        if format == "Latex":
            pass


    @pyqtSlot(QUrl)
    def processAction(self, task):
        # self.mCurrentUrl = task
        #
        # taskMap = {self.parseTask(task)}
        #
        # if taskMap["action"] == "showText":
        #     QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        #     html  = self.documentContent(taskMap, self.ExportFormat.RichText)
        #     QApplication.restoreOverrideCursor()
        #     self.setHtml(html)
        #
        #     record = HistoryRecord()
        #     record.html = html
        #     record.parIds = DocumentBuilder.currentParIds()
        #     record.budIds = DocumentBuilder.currentBudIds()
        #     record.definitionPoint = DocumentBuilder.currentDefinitionPoint()
        #
        #     self.emit(SIGNAL("self.updateHistory(record)"))
        # elif taskMap["action"] == "selectInMap":
        #     self.emit(SIGNAL("self.showParcely(taskMap['ids'].split( ',' ))"))
        # elif taskMap["action"] == "switchPanel":
        #     if taskMap["panel"] == "import":
        #         self.emit(SIGNAL("self.switchToPanelImport()"))
        #     elif taskMap["panel"] == "search":
        #         self.emit(SIGNAL("self.switchToPanelSearch(int(taskMap['type'])"))
        #     self.setHtml(self.mCurrentRecord.html)
        # else:
        #     pass
        pass

    def documentContent(self, taskMap, format):
        format = self.exportFormat()

        doc = VfkDocument(self.documentFactory(format))

        DocumentBuilder.buildHtml(doc, taskMap)
        text = str(doc)

        del doc
        return text

    def exportDocument(self, task, fileName, format):
        fileOut = QFile(fileName)

        if fileOut.open(QIODevice.WriteOnly | QIODevice.Text) is False:
            return False

        taskMap = {}

    def parseTask(self, task):
        # task = QUrl(task)
        # taskList = TaskList(task.encodedQueryItems())
        #
        # taskMap = {'action': task.path()}
        #
        # for i in xrange(len(taskList)):
        #     taskMap[i[0]] = QUrl.fromPercentEncoding(i[1])
        #
        # return taskMap
        pass

    @pyqtSlot()
    def goBack(self):
        pass

    @pyqtSlot()
    def goForth(self):
        pass

    def currentUrl(self):
        return self.mCurrentUrl

    def currentDefinitionPoint(self):
        return self.mCurrentRecord.definitionPoint

    def setConnectionName(self, connectionName):
        pass

    def showInfoAboutSelection(self, parIds, budIds):
        pass

    def showHelpPage(self):
        url = QUrl("showText?page=help")
        self.processAction(url)
