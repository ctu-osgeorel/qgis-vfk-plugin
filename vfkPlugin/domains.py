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


class Domains:

    @staticmethod
    def anoNe(an):
        if an == "a":
            return True
        else:
            return False

    @staticmethod
    def cpCe(kod):
        if kod == 1:
            return "Číslo popisné"
        elif kod == 2:
            return "Číslo evidenční"
        else:
            return ""

    @staticmethod
    def druhUcastnika(kod):
        if kod == 1:
            return "právnická osoba"
        elif kod == 2:
            return "fyzická osoba"
        elif kod == 3:
            return "ostatní"
        elif kod == 4:
            return "právnická osoba státní správy"
        else:
            return ""

    @staticmethod
    def rodinnyStav(kod):
        if kod == 1:
            return "svobodný/svobodná"
        elif kod == 2:
            return "ženatý/vdaná"
        elif kod == 3:
            return "rozvedený/rozvedená"
        elif kod == 4:
            return "ovdovělý/ovdovělá"
        elif kod == 5:
            return "druh/družka"
        else:
            return ""
