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
        if an == u"a":
            return True
        else:
            return False

    @staticmethod
    def cpCe(kod):
        if kod == 1:
            return u"Číslo popisné"
        elif kod == 2:
            return u"Číslo evidenční"
        else:
            return u""

    @staticmethod
    def druhUcastnika(kod):
        if kod == 1:
            return u"právnická osoba"
        elif kod == 2:
            return u"fyzická osoba"
        elif kod == 3:
            return u"ostatní"
        elif kod == 4:
            return u"právnická osoba státní správy"
        else:
            return u""

    @staticmethod
    def rodinnyStav(kod):
        if kod == 1:
            return u"svobodný/svobodná"
        elif kod == 2:
            return u"ženatý/vdaná"
        elif kod == 3:
            return u"rozvedený/rozvedená"
        elif kod == 4:
            return u"ovdovělý/ovdovělá"
        elif kod == 5:
            return u"druh/družka"
        else:
            return u""
