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

from PyQt4.QtCore import qDebug


class ApplyChanges:
    def __init__(self, db_full, db_amendment, db_updated):
        """

        """
        db_full = os.path.abspath(db_full)
        db_amendment = os.path.abspath(db_amendment)
        db_updated = os.path.abspath(db_updated)

        #shutil.copy2(db_full, db_updated)

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

        # process all relevant tables
        for table in table_names:
            # delete old data --> not actual rows
            query = 'DELETE FROM main.{table} ' \
                    'WHERE {column} IN (' \
                    'SELECT DISTINCT t1.{column} FROM main.{table} t1 ' \
                    'JOIN db2.{table} t2 ON t1.{column} = t2.{column})'.format(table=table, column='id')

            qDebug('(VFK) Changes query: {}'.format(query))
            self.cur.execute(query)

            # delete deleted rows
            if table in ['SPOL', 'SOBR']:   # this tables always have actual data
                query = 'DELETE FROM main.{table} ' \
                        'WHERE {column} IN (' \
                        'SELECT DISTINCT t2.{column} FROM db2.{table} t2 ' \
                        'WHERE stav_dat = 0);'.format(table=table, column='id')
            else:
                query = 'DELETE FROM main.{table} ' \
                        'WHERE {column} IN (' \
                        'SELECT DISTINCT t2.{column} FROM db2.{table} t2 ' \
                        'WHERE stav_dat = 3 AND priznak_kontextu = 1);'.format(table=table, column='id')

            qDebug('(VFK) Changes query: {}'.format(query))
            self.cur.execute(query)

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

        for id in ids:
            query = 'INSERT INTO main.{table} ' \
                    'SELECT {columns} FROM db2.{table} ' \
                    'WHERE stav_dat = 0 ' \
                        'AND id = {id} ' \
                    'LIMIT 1;'.format(table=table,
                                                columns=cols.replace('ogr_fid', '\'{ogr_fid}\''.format(ogr_fid=max_fid + 1)),
                                                id=id)

            qDebug('(VFK) Changes query: {}'.format(query))
            self.cur.execute(query)

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
        self.cur.execute(query)

        result = self.cur.fetchall()
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
        self.cur.execute(query)
        result = self.cur.fetchall()

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
        self.cur.execute(query)
        result = self.cur.fetchone()

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
        self.cur.execute(query)
        result = self.cur.fetchall()

        for id in result:
            ids.append(id[0])

        return ids

if __name__ == '__main__':
    ApplyChanges('/home/stepan/GoogleDrive/CVUT/Diplomka/zmenova_data/stav/stavova.db',
                 #'/home/stepan/vfkDB.db',
                 '/home/stepan/GoogleDrive/CVUT/Diplomka/zmenova_data/zmena/zmenova.db',
                 '/home/stepan/Desktop/novaDB.db')
