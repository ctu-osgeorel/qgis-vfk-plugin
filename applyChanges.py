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
import argparse

from PyQt4.QtGui import QWidget, QApplication
from PyQt4.QtCore import qDebug, pyqtSignal, SIGNAL


class ApplyChanges(QWidget):
    # signals
    maxRangeProgressBar = pyqtSignal(int)
    updateStatus = pyqtSignal(int, str)
    finishedStatus = pyqtSignal()
    preprocessingDatabase = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)

        self.__conn = None
        self.__cur = None

    def run(self, db_full, db_amendment, db_updated):
        """

        :param db_full: Path to the main database.
        :param db_amendment: Path to the database with changes to process.
        :param db_updated: Path to the database for export.
        :type db_full: str
        :type db_amendment: str
        :type db_updated: str
        """
        self.emit(SIGNAL('preprocessingDatabase'))

        db_full = os.path.abspath(db_full)
        db_amendment = os.path.abspath(db_amendment)
        db_updated = os.path.abspath(db_updated)

        shutil.copy2(db_full, db_updated)

        # create connection to main database
        self.__conn = sqlite3.connect(db_updated)

        with self.__conn:
            self.__cur = self.__conn.cursor()
            # attach database with amendment data
            self.__cur.execute('ATTACH DATABASE "{}" as db2'.format(db_amendment))

            self.__applyChanges()

        self.emit(SIGNAL('finishedStatus'))

    def __applyChanges(self):
        """
        Method updates rows in main database by rows from databse with amendment data.
        """
        table_names = self.__findTablesWithChanges()
        self.emit(SIGNAL("maxRangeProgressBar"), len(table_names))

        # process all relevant tables
        for i, table in enumerate(table_names):
            self.emit(SIGNAL("updateStatus"), i+1, table)

            # delete old data --> not actual rows
            ### ML: is this really neeed? we could probably implement
            ### also update statements, currently we are performing
            ### only delete and insert statements
            query = 'DELETE FROM main.{table} ' \
                    'WHERE {column} IN (' \
                    'SELECT DISTINCT t1.{column} FROM main.{table} t1 ' \
                    'JOIN db2.{table} t2 ON t1.{column} = t2.{column})'.format(table=table, column='id')

            #qDebug('(VFK) Changes query: {}'.format(query))
            self.__cur.execute(query)

            # delete deleted rows
            if table in ['SPOL', 'SOBR']:   # this tables always have actual data
                ### ML: we are not sure about stav_data = 0 (update vs
                ### delete)
                query = 'DELETE FROM main.{table} ' \
                        'WHERE {column} IN (' \
                        'SELECT DISTINCT t2.{column} FROM db2.{table} t2 ' \
                        'WHERE stav_dat = 0);'.format(table=table, column='id')
            else:
                query = 'DELETE FROM main.{table} ' \
                        'WHERE {column} IN (' \
                        'SELECT DISTINCT t2.{column} FROM db2.{table} t2 ' \
                        'WHERE stav_dat = 3 AND priznak_kontextu = 1);'.format(table=table, column='id')

            #qDebug('(VFK) Changes query: {}'.format(query))
            self.__cur.execute(query)

            self.__doInsertOperation(table)

    def __doInsertOperation(self, table):
        """
        Method will apply operation INSERT into main table.
        Stav dat: 0
        Kontext zmen: 3
        :type table: str
        :return:
        """
        max_fid = self.__getMaxOgrFid(table)
        ids = self.__getListOfIds(table)

        columns = self.__getColumnNames(table)
        # if 'ogr_fid' in columns:
        #     columns.remove('ogr_fid')

        cols = ", ".join(columns)    # create string from list

        qDebug('(VFK) Processing table {}...'.format(table))

        for id in ids:
            ### ML: this operation must be performed on all ids
            ### (currently only the first one is processed)
            query = 'INSERT INTO main.{table} ' \
                    'SELECT {columns} FROM db2.{table} ' \
                    'WHERE stav_dat = 0 ' \
                        'AND id = {id} ' \
                    'LIMIT 1;'.format(table=table,
                                                columns=cols.replace('ogr_fid', '\'{ogr_fid}\''.format(ogr_fid=max_fid + 1)),
                                                id=id)

            #qDebug('(VFK) Changes query: {}'.format(query))
            self.__cur.execute(query)

            max_fid += 1

    def __findTablesWithChanges(self):
        """
        Method finds all tables with some changes in database with amendment data.
        :return: Table names with some changes.
        :rtype: list
        """
        tables = set()
        query = 'SELECT table_name FROM db2.vfk_tables ' \
                'WHERE num_records > 0 OR num_features > 0;'
        self.__cur.execute(query)

        result = self.__cur.fetchall()
        for table in result:
            table = str(table[0])

            # find amendment tables
            columns = self.__getColumnNames(table)
            if 'STAV_DAT' in columns or 'PRIZNAK_KONTEXTU' in columns:
                tables.add(table)

        qDebug('(VFK) Tables with changes: {}'.format(tables))
        return tables

    def __getColumnNames(self, table):
        """
        Get list of columns of given table.
        :param table: Table name
        :type table: str
        :return: list
        """
        columns = []

        query = 'PRAGMA table_info(\'{table}\')'.format(table=table)
        self.__cur.execute(query)
        result = self.__cur.fetchall()

        for row in result:
            columns.append(str(row[1]))

        return columns

    def __getMaxOgrFid(self, table, schema='main'):
        """
        Get max org_fid from given table.
        :param table: Table name
        :param schema: Name of schema
        :type table: str
        :type schema: str
        :return: Maximal ogr_fid
        :rtype: int
        """
        query = 'SELECT max(ogr_fid) FROM {schema}.{table};'.format(table=table, schema=schema)
        self.__cur.execute(query)
        result = self.__cur.fetchone()

        return 0 if result[0] is None else result[0]

    def __getListOfIds(self, table, schema='db2'):
        """
        Get list of ids for given table.
        :param table: Table name
        :param schema: Name of schema
        :type schema: str
        :type table: str
        :return: List of ids
        :rtype: list
        """
        ids = []

        query = 'SELECT DISTINCT id FROM {schema}.{table}'.format(table=table, schema=schema)
        self.__cur.execute(query)
        result = self.__cur.fetchall()

        for id in result:
            ids.append(id[0])

        return ids

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # load arguments from command line
    parser = argparse.ArgumentParser(description='Script applies changes from amendment VFK database to '
                                                 'main VFK database. In this process new database is created.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.1')
    parser.add_argument('-m', '--main', help='Path to the main database.', required=True)
    parser.add_argument('-c', '--changes', help='Path to the database with changes.', required=True)
    parser.add_argument('-e', '--export', help='Path to the new database which will be created.', required=True)

    args = parser.parse_args()

    print('Applying changes..')
    changes = ApplyChanges()
    changes.run(args.main, args.changes, args.export)

    print('--------------------------------')
    print('All changes successfully applied.')
