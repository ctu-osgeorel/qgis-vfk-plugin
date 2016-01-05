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
from PyQt4.QtCore import QFile, QIODevice, QUrl, QObject, SIGNAL, SLOT, pyqtSlot, pyqtSignal, QTextStream, qWarning
from PyQt4.QtSql import QSqlDatabase
from collections import namedtuple

from documentBuilder import *
from htmlDocument import *
from latexDocument import *
from richTextDocument import *


class TPair:
    def __init__(self, first="", second=""):
        self.first = first
        self.second = second


class HistoryRecord:
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

    # signals
    updateHistory = pyqtSignal(QObject)
    showParcely = pyqtSignal(QObject)
    showBudovy = pyqtSignal(QObject)
    currentParIdsChanged = pyqtSignal(bool)
    currentBudIdsChanged = pyqtSignal(bool)
    historyBefore = pyqtSignal(bool)
    historyAfter = pyqtSignal(bool)
    definitionPointAvailable = pyqtSignal(bool)
    switchToPanelImport = pyqtSignal()
    switchToPanelSearch = pyqtSignal(int)

    def __init__(self, parent=None):
        """
        Init function
        """
        super(VfkTextBrowser, self).__init__(parent)

        self.__mCurrentUrl = QUrl()
        self.__mCurrentRecord = HistoryRecord()
        self.__mDocumentBuilder = DocumentBuilder()
        self.__mUrlHistory = []     # list of history records
        self.__mHistoryIt = 0      # saving current index in history list

        self.connect(self, SIGNAL("anchorClicked(QUrl)"), self, SLOT("oLinkClicked(QUrl)"))
        #self.connect(self, SIGNAL("updateHistory(HistoryRecord)"), self.saveHistory(HistoryRecord))

        self.currentParIdsChanged.emit(False)
        self.currentBudIdsChanged.emit(False)
        self.historyBefore.emit(False)
        self.historyAfter.emit(False)

    def currentUrl(self):
        return self.__mCurrentUrl

    def currentParIds(self):
        return self.__mCurrentRecord.parIds

    def currentBudIds(self):
        return self.__mCurrentRecord.budIds

    def currentDefinitionPoint(self):
        return self.__mCurrentRecord.definitionPoint

    def startPage(self):
        self.processAction(QUrl("showText?page=allTEL"))

    def exportDocument(self, task, fileName, format):
        """

        :param task: QUrl
        :param fileName: str
        :param format: self.ExportFormat
        :return: bool
        """
        fileOut = QFile(fileName)

        if fileOut.open(QIODevice.WriteOnly | QIODevice.Text) is False:
            return False

        taskMap = self.__parseTask(task)
        text = self.__documentContent(taskMap, format)
        streamFileOut = QTextStream(fileOut)
        streamFileOut.setCodec("UTF-8")
        streamFileOut << text
        streamFileOut.flush()

        fileOut.close()

        return True

    def setConnectionName(self, connectionName):
        """

        :param connectionName: str
        """
        self.__mDocumentBuilder = DocumentBuilder(connectionName)

    def __parseTask(self, task):
        """

        :param task: QUrl
        :return: dict
        """
        taskMap = {'action': task.path()}

        for key, value in task.encodedQueryItems():
            taskMap[str(key)] = QUrl.fromPercentEncoding(value)

        return taskMap

    @pyqtSlot()
    def goBack(self):
        qWarning("...goBack function")
        # if self.__mHistoryIt != self.__mUrlHistory[0]:
        #     qWarning("..podminka v goBack splnena")
        #     #self.__mCurrentRecord = self.__mUrlHistory[self.__mHistoryIt]
        #     self.setHtml(self.__mCurrentRecord.html)
        #     self.updateButtonEnabledState()

    @pyqtSlot()
    def goForth(self):
        qWarning("...goForth function")
        # if self.__mHistoryIt != self.__mUrlHistory[-2]:
        #     qWarning("..podminka v goForth splnena")
        #     #self.__mCurrentRecord = self.__mUrlHistory[self.__mHistoryIt]
        #     self.setHtml(self.__mCurrentRecord.html)
        #     self.updateButtonEnabledState()


    def saveHistory(self, record):
        pass



# void VfkTextBrowser::saveHistory( HistoryRecord record )
# {
#   if ( mUrlHistory.isEmpty() )
#   {
#     mUrlHistory.append( record );
#     mHistoryIt = mUrlHistory.begin();
#   }
#   else if ( mHistoryIt == --mUrlHistory.end() )
#   {
#     mUrlHistory.append( record );
#     mHistoryIt = --(mUrlHistory.end());
#   }
#   else
#   {
#     mUrlHistory.erase( ++mHistoryIt, mUrlHistory.end() );
#     mUrlHistory.append( record );
#     mHistoryIt = --(mUrlHistory.end());
#   }
#   mCurrentRecord = *mHistoryIt;
#   updateButtonEnabledState();
# }

    def showHelpPage(self):
        qWarning("..VfkTextBrowser.showHelpPage()")
        url = "showText?page=help"
        self.processAction(QUrl(url))


    def showInfoAboutSelection(self, parIds, budIds):
        """

        :param parIds: list
        :param budIds: list
        :return:
        """
        url = ""
        if len(parIds) + len(budIds) == 1:
            if len(parIds) == 1:
                url = "showText?page=par&id={}".format(parIds[0])
            else:
                url = "showText?page=bud&id={}".format(budIds[0])

            self.processAction(QUrl(url))
            return

        urlPart = ""
        if len(parIds) > 0:
            urlPart = "&parcely={}".format(", ".join(parIds))
        if len(budIds) > 0:
            urlPart = "&budovy={}".format(", ".join(budIds))
        if urlPart:
            url = "showText?page=seznam&type=id{}".format(urlPart)
            self.processAction(QUrl(url))

    def postInit(self):
        self.currentParIdsChanged.emit(False)
        self.currentBudIdsChanged.emit(False)
        self.historyBefore.emit(False)
        self.historyAfter.emit(False)
        self.definitionPointAvailable.emit(False)

    def documentFactory(self, format):
        """

        :param format: VfkTextBrowser.ExportFormat
        :rtype: VfkDocument
        """
        doc = VfkDocument()

        if format == VfkTextBrowser.ExportFormat.Latex:
            doc = LatexDocument()
            return doc
        elif format == VfkTextBrowser.ExportFormat.Html:
            doc = HtmlDocument()
            return doc
        elif format == VfkTextBrowser.ExportFormat.RichText:
            doc = RichTextDocument()
            return doc
        else:
            qWarning("Nejsou podporovany jine formaty pro export")

    def updateButtonEnabledState(self):
        self.currentParIdsChanged.emit(True if self.__mCurrentRecord.parIds else False)
        self.currentBudIdsChanged.emit(True if self.__mCurrentRecord.budIds else False)
        self.historyBefore.emit() ##### dodelat
        self.historyAfter.emit() ##### dodelat
        self.definitionPointAvailable.emit(True if (self.__mCurrentRecord.definitionPoint.first
                                                    and self.__mCurrentRecord.definitionPoint.second) else False)

    def onLinkClicked(self, task):
        """

        :param task: QUrl
        """
        qWarning("..onLinkClicked")
        self.processAction(task)

    def processAction(self, task):
        """

        :param task: QUrl
        """
        self.__mCurrentUrl = task

        qWarning("..VfkTextBrowser.processAction()")

        taskMap = self.__parseTask(task)

        if taskMap["action"] == "showText":
            qWarning("...............showText ano")
            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            t = QtCore.QTime()
            t.start()
            html = self.__documentContent(taskMap, self.ExportFormat.RichText)
            qWarning("Total time elapsed: {} ms".format(t.elapsed()))
            QApplication.restoreOverrideCursor()
            self.setHtml(html)

            record = HistoryRecord()
            record.html = html
            record.parIds = self.__mDocumentBuilder.currentParIds()
            record.budIds = self.__mDocumentBuilder.currentBudIds()
            record.definitionPoint = self.__mDocumentBuilder.currentDefinitionPoint()

            #self.updateHistory.emit(record)

        elif taskMap["action"] == "selectInMap":
            self.showParcely.emit(taskMap['ids'].split(','))
        elif taskMap["action"] == "switchPanel":
            if taskMap["panel"] == "import":
                self.switchToPanelImport.emit()
            elif taskMap["panel"] == "search":
                self.switchToPanelSearch.emit(int(taskMap['type']))
            self.setHtml(self.__mCurrentRecord.html)
        else:
            qWarning("..Jina akce")

    def __documentContent(self, taskMap, format):
        """

        :param taskMap: dict
        :param format: VfkTextBrowser.ExportFormat
        :return:
        """
        doc = self.documentFactory(format)
        if not doc:
            return ""

        self.__mDocumentBuilder.buildHtml(doc, taskMap)
        text = str(doc)

        return text
