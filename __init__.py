# -*- coding: utf-8 -*-
"""
/***************************************************************************
 vfkPlugin
                                 A QGIS plugin
 Plugin umoznujici praci s daty katastru nemovitosti
                             -------------------
        begin                : 2015-06-11
        copyright            : (C) 2015 by Stepan Bambula
        email                : stepan.bambula@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import


def classFactory(iface):
    from .vfkPlugin import vfkPlugin
    return vfkPlugin(iface)
