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

from PyQt4.QtCore import QThread, pyqtSignal


class OpenThread(QThread):
    working = pyqtSignal(str)

    def __init__(self, fileName):
        """
        Class for using multi-thread import of layers
        :type fileName: str
        :return:
        """
        QThread.__init__(self)

        self.fileName = fileName

    def run(self):
        self.working.emit(self.fileName)
