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
from __future__ import print_function
from builtins import str
from builtins import zip

import sqlite3
import sys
import os
import shutil
import argparse
from datetime import datetime

from qgis.PyQt.QtWidgets import QWidget, QApplication
from qgis.PyQt.QtCore import qDebug, pyqtSignal


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
        self.__use_debug = False

    def run(self, db_full, db_amendment, db_updated, use_debug=False):
        """

        :param db_full: Path to the main database.
        :param db_amendment: Path to the database with changes to process.
        :param db_updated: Path to the database for export.
        :param use_debug: True if queries will be debugged.
        :type db_full: str
        :type db_amendment: str
        :type db_updated: str
        """
        self.preprocessingDatabase.emit()

        db_full = os.path.abspath(db_full)
        db_amendment = os.path.abspath(db_amendment)
        db_updated = os.path.abspath(db_updated)

        self.__use_debug = use_debug

        qDebug('(VFK) Preparing databases..')
        # copy main database
        shutil.copy2(db_full, db_updated)

        # create connection to main database
        self.__conn = sqlite3.connect(db_updated)

        with self.__conn:
            self.__cur = self.__conn.cursor()

            # attach database with amendment data
            query = 'ATTACH DATABASE "{}" as db2'.format(db_amendment)
            self.__doQuery(query)

            self.__applyChanges()

        self.finishedStatus.emit()

    def __applyChanges(self):
        """
        Method updates rows in main database by rows from databse with amendment data.
        """
        table_names = self.__findTablesWithChanges()
        self.maxRangeProgressBar.emit(len(table_names))

        # process all relevant tables
        for i, table in enumerate(table_names):
            self.updateStatus.emit(i+1, table)

            # Delete data which are in both databases --> there are updates in amendment database
            query = 'DELETE FROM main.{table} ' \
                    'WHERE id IN (' \
                    'SELECT DISTINCT t1.id FROM main.{table} t1 ' \
                    'JOIN db2.{table} t2 ON t1.id = t2.id)'.format(table=table)

            self.__doQuery(query)

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

        qDebug('(VFK) Processing table {}..'.format(table))

        for id in ids:
            # get all rows for given ID
            query = 'SELECT * FROM db2.{table} WHERE stav_dat=0 AND id={id}'.format(table=table, id=id)
            self.__doQuery(query)
            result = self.__cur.fetchall()

            if len(result) > 0:
                # create list of dictionaries from returned rows
                data_rows = []
                for row in result:
                    tmp = []
                    for item in row:
                        tmp.append(item)

                    data_rows.append(dict(list(zip(columns, tmp))))

                # sort data according to the date 'DATUM_VZNIKU'
                if 'DATUM_VZNIKU' in data_rows[0]:
                    data_rows.sort(key=lambda x: datetime.strptime(x['DATUM_VZNIKU'], '%d.%m.%Y %H:%M:%S'), reverse=True)

                # insert new data into main table
                selected_ogr_fid = data_rows[0]['ogr_fid']

                query = 'INSERT INTO main.{table} ' \
                        'SELECT {columns} FROM db2.{table} ' \
                        'WHERE ogr_fid={selected_ogr_fid} ' \
                        'AND stav_dat=0 ' \
                        'AND id = {id};'.format(table=table,
                                          columns=cols.replace('ogr_fid', '\'{ogr_fid}\''.format(ogr_fid=max_fid + 1)),
                                          selected_ogr_fid=selected_ogr_fid,
                                          id=id)

                self.__doQuery(query)
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
        self.__doQuery(query)

        result = self.__cur.fetchall()
        for table in result:
            table = str(table[0])

            # find amendment tables
            columns = self.__getColumnNames(table)
            if 'STAV_DAT' in columns or 'PRIZNAK_KONTEXTU' in columns:
                tables.add(table)

        qDebug('(VFK) Tables with changes: {}'.format(', '.join(x for x in tables)))
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
        self.__doQuery(query)
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
        self.__doQuery(query)
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
        self.__doQuery(query)
        result = self.__cur.fetchall()

        for id in result:
            ids.append(id[0])

        return ids

    def __doQuery(self, query):
        """
        Method will execute given query in opened database.
        :param query: Query
        """
        if self.__use_debug:
            qDebug('(VFK) Apply changes query: {}'.format(query))

        self.__cur.execute(query)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # load arguments from command line
    description = 'Script applies changes from amendment VFK database to ' \
                  'main VFK database. In this process new database is created.'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.1')
    parser.add_argument('-i', '--input', help='Path to the main database.', required=True)
    parser.add_argument('-c', '--changes', help='Path to the database with changes.', required=True)
    parser.add_argument('-o', '--output', help='Path to the new database which will be created.', required=True)
    parser.add_argument('-d', '--debug', help='Enables debug mode.', action='store_true')

    args = parser.parse_args()

    if args.debug:
        use_debug = args.debug
    else:
        use_debug = False

    print('Applying changes..')
    print('------------------')
    changes = ApplyChanges()
    changes.run(args.input, args.changes, args.output, use_debug)

    print('--------------------------------')
    print('All changes successfully applied.')
