#!/usr/bin/python
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

import sqlite3
import sys
import os
import shutil


class ApplyChanges:
    def __init__(self, db_full, db_amendment, db_updated):
        """

        """
        db_full = os.path.abspath(db_full)
        db_amendment = os.path.abspath(db_amendment)
        db_updated = os.path.abspath(db_updated)

        shutil.copy2(db_full, db_updated)

        # create connection to main database
        self.conn = sqlite3.connect(db_updated)

        with self.conn:

            self.cur = self.conn.cursor()
            # attach database with amendment data
            self.cur.execute('ATTACH DATABASE "{}" as db2'.format(db_amendment))

            self.applyChanges()

    def applyChanges(self):
        """
        Method updates rows in main database by rows from databse with amendment data.
        """
        table_names = self.__findTablesWithChanges()
        print table_names


    def __findTablesWithChanges(self):
        """
        Method finds all tables with some changes in database with amendment data.
        :return: Table names with some changes.
        :rtype: list
        """
        tables = []
        query = 'SELECT table_name FROM db2.vfk_tables ' \
                'WHERE num_records > 0;'
        self.cur.execute(query)

        data = self.cur.fetchall()
        for table in data:
            tables.append(str(table[0]))

        return tables


if __name__ == '__main__':
    ApplyChanges(#'/home/stepan/GoogleDrive/CVUT/Diplomka/zmenova_data/stav/stavova.db',
                 '/home/stepan/vfkDB.db',
                 '/home/stepan/GoogleDrive/CVUT/Diplomka/zmenova_data/zmena/zmenova.db',
                 '/home/stepan/Desktop/novaDB.db')
