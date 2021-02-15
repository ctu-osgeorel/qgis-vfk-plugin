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
from builtins import range
from qgis.PyQt.QtCore import QRegExp
from .vfkDocument import *


class RichTextDocument(VfkDocument):
    # static variables
    defaultTableAttributes = "border=\"0\" cellspacing=\"1px\" cellpadding=\"0\""
    defaultCssStyle = """
        body{
          background-color: white;
          color: black;
        }
        table th{
          background-color: #ffbb22;
          padding: 3px;
        }
        table td{
          padding: 3px;
        }
        table tr td.oddRow{
          background-color: #ffff55;
        }
        table tr td.evenRow{
          background-color: #ffff99;
        }"""

    def __init__(self):
        super(RichTextDocument, self).__init__()
        self.__mPage = u""
        self.__mLastColumnNumber = 0
        self.__mCurrentTableRowNumber = 0

    def __currentTableRowCssClass(self):
        return u"evenRow" if self.__mCurrentTableRowNumber % 2 == 0 else u"oddRow"

    def toString(self):
        return self.__mPage

    def header(self):
        self.__mPage += u"<html><head>"
        self.__mPage += u"<style>" + self.defaultCssStyle + u"</style>"
        self.__mPage += u"</head><body>"

    def footer(self):
        self.__mPage += u"</body></html>"

    def heading1(self, text):
        self.__mPage += u"<h1>{}</h1>".format(text)

    def heading2(self, text):
        self.__mPage += u"<h2>{}</h2>".format(text)

    def heading3(self, text):
        self.__mPage += u"<h3>{}</h3>".format(text)

    def beginItemize(self):
        self.__mPage += u"<ul>"

    def endItemize(self):
        self.__mPage += u"</ul>"

    def beginItem(self):
        self.__mPage += u"<li>"

    def endItem(self):
        self.__mPage += u"</li>"

    def item(self, text):
        self.__mPage += u"<li>{}</li>".format(text)

    def beginTable(self):
        self.__mPage += u"<table " + self.defaultTableAttributes + u">"
        self.__mCurrentTableRowNumber = 1

    def endTable(self):
        self.__mPage += u"</table>"

    def tableHeader(self, columns):
        self.__mPage += u"<tr>"

        for column in columns:
            self.__mPage += u"<th>{}</th>".format(column)

        self.__mPage += u"</tr>"
        self.__mLastColumnNumber = len(columns)

    def tableRow(self, columns):
        self.__mPage += u"<tr>"

        for column in columns:
            self.__mPage += u"<td class=\"{}\">{}</td>".format(
                self.__currentTableRowCssClass(), column)

        self.__mPage += u"</tr>"
        self.__mLastColumnNumber = len(columns)
        self.__mCurrentTableRowNumber += 1

    def tableRowOneColumnSpan(self, text):
        self.__mPage += u"<tr>"
        self.__mPage += u"<td colspan=\"{}\" class=\"{}\">{}</td>".format(self.__mLastColumnNumber,
                                                                          self.__currentTableRowCssClass(), text)
        self.__mPage += u"</tr>"
        self.__mCurrentTableRowNumber += 1

    def link(self, href, text):
        return u"<a href=\"{}\">{}</a>".format(href, text)

    def superScript(self, text):
        return u"<sup>{}</sup>".format(text)

    def newLine(self):
        return u"<br/>"

    def keyValueTable(self, content):
        self.beginTable()

        for it in content:
            self.tableRow([it.first, it.second])

        self.endTable()

    def paragraph(self, text):
        self.__mPage += u"<p>{}</p>".format(text)

    def table(self, content, header):
        """
        :param content: list
        :param header: bool
        """
        self.beginTable()
        i = 0
        if header and content:
            self.tableHeader(content[0])
            i += 1

        for j in range(i, len(content)):
            self.tableRow(content[j])

        self.endTable()

    def text(self, text):
        self.__mPage += text

    def discardLastBeginTable(self):
        index = self.__mPage.rfind("<table")
        self.__mPage = self.__mPage[:index]

    def isLastTableEmpty(self):
        if self.__mPage.find(QRegExp("<table[^>]*>$")) != -1:
            return True
        else:
            return False
