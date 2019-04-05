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
from builtins import object
from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class TPair(object):

    def __init__(self, first=u'', second=u''):
        self.first = first
        self.second = second


class VfkDocument(with_metaclass(ABCMeta, object)):

    def __init__(self):
        pass

    @abstractmethod
    def header(self):
        pass

    @abstractmethod
    def footer(self):
        pass

    @abstractmethod
    def heading1(self, text):
        pass

    @abstractmethod
    def heading2(self, text):
        pass

    @abstractmethod
    def heading3(self, text):
        pass

    @abstractmethod
    def beginItemize(self):
        pass

    @abstractmethod
    def endItemize(self):
        pass

    @abstractmethod
    def beginItem(self):
        pass

    @abstractmethod
    def endItem(self):
        pass

    @abstractmethod
    def item(self, text):
        pass

    @abstractmethod
    def beginTable(self):
        pass

    @abstractmethod
    def endTable(self):
        pass

    @abstractmethod
    def tableHeader(self, columns):
        pass

    @abstractmethod
    def tableRow(self, columns):
        pass

    @abstractmethod
    def tableRowOneColumnSpan(self, text):
        pass

    @abstractmethod
    def link(self, href, text):
        pass

    @abstractmethod
    def superScript(self, text):
        pass

    @abstractmethod
    def newLine(self):
        pass

    @abstractmethod
    def keyValueTable(self, content):
        pass

    @abstractmethod
    def paragraph(self, text):
        pass

    @abstractmethod
    def table(self, content, header):
        pass

    @abstractmethod
    def text(self, text):
        pass

    @abstractmethod
    def discardLastBeginTable(self):
        pass

    @abstractmethod
    def isLastTableEmpty(self):
        pass
