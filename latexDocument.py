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
from __future__ import absolute_import
from builtins import map
from builtins import range

from qgis.PyQt.QtCore import qDebug
from .vfkDocument import VfkDocument


class LatexDocument(VfkDocument):

    def __init__(self):
        super(LatexDocument, self).__init__()

        # local variables
        self.__mPage = u''
        self.__mLastTableContent = []
        self.__mLastTableHeader = u''
        self.__mLastColumnNumber = 0
        self.__mMaxRows = 20

    def toString(self):
        return self.__mPage

    def header(self):
        self.__mPage += u'''
\documentclass[a4paper,9pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[czech]{babel}
\\usepackage{a4wide}
\\usepackage{tabulary}
\\begin{document}\n'''

    def footer(self):
        self.__mPage += u"\end{document}\n"

    def heading1(self, text):
        self.__mPage += u"\section*{%s}\n" % text

    def heading2(self, text):
        self.__mPage += u"\subsection*{%s}\n" % text

    def heading3(self, text):
        self.__mPage += u"\subsubsection*{%s}\n" % text

    def beginItemize(self):
        self.__mPage += u"\\begin{itemize}\n"

    def endItemize(self):
        self.__mPage += u"\end{itemize}\n"

    def beginItem(self):
        self.__mPage += u"\item "

    def endItem(self):
        self.__mPage += u"\\n"

    def item(self, text):
        self.__mPage += u"\item %s \n" % text

    def beginTable(self):
        self.__mLastTableHeader = u''
        self.__mLastTableContent = []

    def endTable(self):
        table = u''

        if self.__mLastColumnNumber > 0:
            tooLongTable = False if len(
                self.__mLastTableContent) < self.__mMaxRows else True
            beginTable = u"\\begin{tabulary}{\\textwidth}{"
            endTable = u"\end{tabulary}\n"
            header = self.__mLastTableHeader + u"\\\\ \hline \hline\n"

            for i in range(self.__mLastColumnNumber):
                beginTable += u"L"
            beginTable += u"}\n"

            if tooLongTable:
                rows = 0

                while rows + self.__mMaxRows < len(self.__mLastTableContent):
                    table += beginTable
                    table += header

                    for i in range(rows, rows + self.__mMaxRows):
                        table += self.__mLastTableContent[i]
                        table += u"\\\\ \n"

                    table += endTable
                    table += u" \\newpage\n"
                    rows += self.__mMaxRows

                table += beginTable
                table += header

                for i in range(rows, len(self.__mLastTableContent)):
                    table += self.__mLastTableContent[i]
                    table += u"\\\\ \n"

                table += endTable
            else:
                table += beginTable
                table += header
                table += u"\\\\ \n".join(
                    map(str, self.__mLastTableContent))
                table += endTable
        self.__mPage += table

    def tableHeader(self, columns):
        self.__mLastColumnNumber = len(columns)
        if self.__mLastColumnNumber > 0:
            tableHeader = u''

            for it in columns:
                columnHeader = u"\\textbf{%s} & " % it
                words = u' '.split(it)
                if len(words) == 1:
                    columnHeader = u"\mbox{\\textbf{%s}} & " % it
                tableHeader += columnHeader

            tableHeader = tableHeader[:-2]
            self.__mLastTableHeader = tableHeader

    def tableRow(self, columns):
        if self.__mLastColumnNumber != len(columns):
            qDebug("inconsistent number of columns: {} {}".format(
                self.__mLastColumnNumber, len(columns)))
            return
        if self.__mLastColumnNumber > 0:
            tableRow = u'{} '.format(columns[0])

            for it in columns:
                tableRow += u"& {} ".format(it)

            self.__mLastTableContent.append(tableRow)

    def tableRowOneColumnSpan(self, text):
        if self.__mLastColumnNumber != 0:
            self.__mLastTableContent.append(
                u"\multicolumn{%s}{l}{%s}" % (self.__mLastColumnNumber, text))

    def link(self, href, text):
        return text

    def superScript(self, text):
        return u"$^{%s}$" % text

    def newLine(self):
        return u"\\newline\n"

    def keyValueTable(self, content):
        self.__mPage += u"\\begin{tabulary}{\\textwidth}{LL}\n"

        for it in content:
            self.__mPage += u"\\textbf{%s} & %s \\\\ \n" % (
                it.first, it.second)

        self.__mPage += u"\end{tabulary}\n"

    def paragraph(self, text):
        self.__mPage += u"\n%s\n" % text

    def table(self, content, header):
        self.beginTable()
        i = 0

        if header and content:
            self.tableHeader(content[0])
            i += 1

        for j in range(i, len(content)):
            self.tableRow(content[j])

        self.endTable()

    def text(self, text):
        self.__mPage += u"%s\n" % text

    def discardLastBeginTable(self):
        pass

    def isLastTableEmpty(self):
        return False
