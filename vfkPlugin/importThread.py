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
import time


class ImportThread(QThread):
    importFinished = pyqtSignal()
    importStatus = pyqtSignal(int, int)

    def __init__(self, layers):
        """
        Class for using multi-thread import of layers
        :type layers: list
        :return:
        """
        QThread.__init__(self)
        self.layers = layers

    def run(self):
        n = len(self.layers)

        for i in range(0, n):
            self.importStatus.emit(i, n)
            time.sleep(0.05)

        self.importFinished.emit()
