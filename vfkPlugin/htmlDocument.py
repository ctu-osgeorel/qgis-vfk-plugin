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


from PyQt4.QtCore import QRegExp
from PyQt4.Qt import QTableWidget

from vfkDocument import VfkDocument

class HtmlDocument(VfkDocument):
    def __init__(self):
        self.mPage = ''
        self.mLastColumnNumber = -1
        self.titleIsSet = False
    
    def toString(self):
        page = '<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 3.2 Final//EN\">'
        page += self.mPage
        page.replace("&", "&amp;")
        page.replace( QRegExp( "<a[^>]*>([^<]*)</a>" ), "\\1" )
        
        return page
    
    def header(self):
        mPage += '''
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

        self.titleIsSet = False;
    
    def footer(self):
        self.mPage += "</body></html>"
        
    def heading1(self, text):
        self.mPage += "<h1>{}</h1>".format(text)

        if titleIsSet is False:
          title( text );
          
    def heading2(self, text):
        self.mPage += "<h2>{}</h2>".format(text)
        
    def heading3(self, text):
        self.mPage += "<h3>{}</h3>".format(text)
        
    def beginItemize(self):
        self.mPage += "<ul>"
        
    def endItemize(self):
        self.mPage += "</ul>"
        
    def beginItem(self):
        self.mPage += "<li>"
        
    def endItem(self):
        self.mPage += "</li>"
        
    def beginTable(self):
        self.mPage += "<table>"    
        
    def endTable(self):
        self.mPage += "</table>"
        
    def tableHeader(self, columns):
        self.mPage += "<tr>"
        
        for column in columns:
          self.mPage += "<th>{}</th>".format(column)
        
        self.mPage += "</tr>"
        self.mLastColumnNumber = len(columns)
        
    def tableRow(self, columns):
        self.mPage += "<tr>"
        
        for column in columns:
          self.mPage += "<td>{}</td>".format(column)
        
        self.mPage += "</tr>"        
        self.mLastColumnNumber = len(columns)
        
    def tableRowOneColumnSpan(self, text):
        self.mPage += "<tr>"
        self.mPage += "<td colspan=\"{}\">{}</td>".format(mLastColumnNumber, text)
        self.mPage += "</tr>"
        
        
    def link(self, href, text):
        return "<a href=\"{}\">{}</a>".format(href, text)
        
    def superscript(self, text):
        return "<sup><small>{}</small></sup>".format(text)
    
    def newLine(self):
        return "<br/>"
    
    def keyValueTable(self, content):
        self.mPage += "<table>"
        
        for i in content:        
          self.mPage += "<tr>"
          self.mPage += "<td>{}</td>".format(i[0])
          self.mPage += "<td>{}</td>".format(i[1])
          self.mPage += "</tr>"
        
        self.mPage += QString( "</table>" )
    
    def paragraph(self, text):
        self.mPage += "<p>{}</p>".format(text)
        
    def table(self, content, header):        
        self.beginTable();
        
        for i, cont in enumerate(content):
            if i == 0 and header and content != "":
                self.tableHeader(content[0])            
            
            self.tableRow(content[i])        
        
        endTable()
        
    def text(self, text):
        self.mPage += text
        
#     def discardLastBeginTable(self):
#         index = self.mPage.lastIndexOf("<table")
#         self.mPage.chop( mPage.size() - index )
        
        
    def isLastTableEmpty(self):
        if self.mPage.find("<table[^>]*>$") != -1:
            return True
        else:
            return False
    
    def title(self, text):
        self.mPage.replace("<title>.*</title>", "<title>{}</title>".format(text))
        self.titleIsSet = True
        
        
        
        
        