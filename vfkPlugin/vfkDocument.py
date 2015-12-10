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


class TPair:
    def __init__(self, first="", second=""):
        self.first = first
        self.second = second


class VfkDocument():
    def __init__(self):
        pass

    def header(self):
        pass

    def footer(self):
        pass

    def heading1(self, text):
        pass

    def heading2(self, text):
        pass

    def heading3(self, text):
        pass

    def beginItemize(self):
        pass

    def endItemize(self):
        pass

    def beginItem(self):
        pass

    def endItem(self):
        pass

    def item(self, text):
        pass

    def beginTable(self):
        pass

    def endTable(self):
        pass

    def tableHeader(self, columns):
        pass

    def tableRow(self, columns):
        pass

    def tableRowOneColumnSpan(self, text):
        pass

    def link(self, href, text):
        pass

    def superScript(self, text):
        pass

    def newLine(self):
        pass

    def keyValueTable(self, content):
        pass

    def paragraph(self, text):
        pass

    def table(self, content, header):
        pass

    def text(self, text):
        pass

    def discardLastBeginTable(self):
        pass

    def isLastTableEmpty(self):
        pass
