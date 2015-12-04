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
from PyQt4.QtCore import QFile, QIODevice, QUrl, SIGNAL, SLOT
from PyQt4.QtSql import QSqlDatabase

from vfkDocument import *
from documentBuilder import *


class Coordinates:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0


class HistoryRecord:
    def __init__(self):
        self.html = ""
        self.parIds = []
        self.budIds = []
        self.definitionPoint = Coordinates()


class vfkTextBrowser(QTextBrowser):

    class ExportFormat(object):
        Html = 0
        RichText = 1
        Latex = 2

    def __init__(self):
        super(vfkTextBrowser, self).__init__()

        self.mCurrentUrl = QUrl()
        self.mCurrentRecord = HistoryRecord()

    # signals
    @staticmethod
    def updateHistory(HistoryRecord): pass
    @staticmethod
    def showParcely(QStringList): pass
    @staticmethod
    def showBudovy(QStringList): pass

    def startPage(self):
        self.processAction(QUrl("showText?page=allTEL"))

    def documentFactory(self, format):
        format = self.ExportFormat()

        doc = VfkDocument()

        if format == "Latex":
            pass



    def processAction(self, task):
        self.mCurrentUrl = task
        taskMap = {self.parseTask(task)}

        if taskMap["action"] == "showText":
            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            html  = self.documentContent(taskMap, self.ExportFormat.RichText)
            QApplication.restoreOverrideCursor()
            self.setHtml(html)

            record = HistoryRecord()
            record.html = html
            record.parIds = DocumentBuilder.currentParIds()
            record.budIds = DocumentBuilder.currentBudIds()
            record.definitionPoint = DocumentBuilder.currentDefinitionPoint()

            self.emit(SIGNAL("self.updateHistory(record)"))
        elif taskMap["action"] == "selectInMap":
            self.emit(SIGNAL("self.showParcely(taskMap['ids'].split( ',' ))"))
        elif taskMap["action"] == "switchPanel":
            if taskMap["panel"] == "import":
                self.emit(SIGNAL("self.switchToPanelImport()"))
            elif taskMap["panel"] == "search":
                self.emit(SIGNAL("self.switchToPanelSearch(int(taskMap['type'])"))
            self.setHtml(self.mCurrentRecord.html)
        else:
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
        task = QUrl(task)
        taskList = [task.encodedQueryItems()]
        taskMap = {'action': task.path()}

        for i, value in enumerate(taskList):
            taskMap[value[0]] = QUrl.fromPercentEncoding(value[1])

        return taskMap

    def goBack(self):
        pass

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