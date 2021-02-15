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

from .vfkDocument import VfkDocument


class HtmlDocument(VfkDocument):

    def __init__(self):
        super(HtmlDocument, self).__init__()
        self.__mPage = ''
        self.__mLastColumnNumber = -1
        self.titleIsSet = False

    def toString(self):
        page = u'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        page += self.__mPage
        page.replace(u"&", u"&amp;")
        page.replace(u"<a[^>]*>([^<]*)</a>", u"\1")

        return page

    def header(self):
        self.__mPage += '''
          <html><head>
          <meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">
          <meta http-equiv=\"content-language\" content=\"cs\">
          <title></title>
          <style type=\"text/css\">
          body{
            background-color: white;
            color: black;
          }
          table tr:nth-child(odd) td{
            background-color: #ffff55;
          }
          table tr:nth-child(even) td{
            background-color: #ffff99;
          }
          table th{
            background-color: #ffbb22;
          }
          table{
          border: 0;
            border-collapse:collapse;
            border:1px solid #ffbb1d;
            margin:0px 0px;
          }
          table td, table th{
            padding-left: 0.5em;
            padding-right: 0.5em;
            padding-top: 0.2em;
            padding-bottom: 0.2em;
          }
          </style>
          </head><body>'''

        self.titleIsSet = False

    def footer(self):
        self.__mPage += u"</body></html>"

    def heading1(self, text):
        self.__mPage += u"<h1>{}</h1>".format(text)

        if not self.titleIsSet:
            self.title(text)

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
        self.__mPage += u"<table>"

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
            self.__mPage += u"<td>{}</td>".format(column)

        self.__mPage += u"</tr>"
        self.__mLastColumnNumber = len(columns)

    def tableRowOneColumnSpan(self, text):
        self.__mPage += u"<tr>"
        self.__mPage += u"<td colspan=\"{}\">{}</td>".format(
            self.__mLastColumnNumber, text)
        self.__mPage += u"</tr>"

    def link(self, href, text):
        return u"<a href=\"{}\">{}</a>".format(href, text)

    def superScript(self, text):
        return u"<sup><small>{}</small></sup>".format(text)

    def newLine(self):
        return u"<br/>"

    def keyValueTable(self, content):
        self.__mPage += u"<table>"

        for i in content:
            self.__mPage += u"<tr>"
            self.__mPage += u"<td>{}</td>".format(i.first)
            self.__mPage += u"<td>{}</td>".format(i.second)
            self.__mPage += u"</tr>"

        self.__mPage += u"</table>"

    def paragraph(self, text):
        self.__mPage += u"<p>{}</p>".format(text)

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
        self.__mPage += text

    def discardLastBeginTable(self):
        index = self.__mPage.rfind(u"<table")
        self.__mPage = self.__mPage[:index]

    def isLastTableEmpty(self):
        if self.__mPage.find(u"<table[^>]*>$") != -1:
            return True
        else:
            return False

    def title(self, text):
        self.__mPage.replace(
            u"<title>.*</title>", u"<title>{}</title>".format(text))
        self.titleIsSet = True
