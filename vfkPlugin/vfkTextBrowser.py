# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import QFile, QIODevice, QUrl
from PyQt4.QtSql import QSqlDatabase


class HistoryRecord:
        def __init__(self):
            self.html = ""
            self.parIds = []
            self.budIds = []
            self.definitionPoint = {'x': 0, 'y': 0}


class vfkTextBrowser(QTextBrowser):

    def __init__(self):
        self.mCurrentUrl = QUrl()
        self.mCurrentRecord = HistoryRecord()

    def exportDocument(self, task, fileName, format):
        fileOut = QFile(fileName)

        if fileOut.open(QIODevice.WriteOnly | QIODevice.Text) is False:
            return False

        taskMap = {}


    def parseTask(self, task):
        task = QUrl(task)
        taskList = []
        taskList.append(task.encodedQueryItems())

        taskMap = {}
        taskMap['action'] = task.path()

        for i in taskList:
            taskMap['']

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