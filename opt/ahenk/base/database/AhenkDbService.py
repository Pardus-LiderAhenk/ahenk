#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import sqlite3

from base.Scope import Scope


class AhenkDbService(object):
    """
        Sqlite manager for ahenk
    """

    def __init__(self):
        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        self.db_path = self.configurationManager.get('BASE', 'dbPath')
        self.connection = None
        self.cursor = None

    def initialize_table(self):
        self.check_and_create_table('task', ['id INTEGER', 'create_date TEXT', 'modify_date TEXT', 'command_cls_id TEXT', 'parameter_map BLOB', 'deleted INTEGER', 'plugin TEXT'])
        self.check_and_create_table('policy', ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'type TEXT', 'version TEXT', 'name TEXT'])
        self.check_and_create_table('profile', ['id INTEGER', 'create_date TEXT', 'label TEXT', 'description TEXT', 'overridable INTEGER', 'active INTEGER', 'deleted INTEGER', 'profile_data TEXT', 'modify_date TEXT', 'plugin TEXT'])
        self.check_and_create_table('plugin', ['version TEXT', 'name TEXT', 'description TEXT'])
        self.check_and_create_table('registration', ['jid TEXT', 'password TEXT', 'registered INTEGER', 'dn TEXT', 'params TEXT', 'timestamp TEXT'])

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.logger.error('Database connection error ' + str(e))

    def check_and_create_table(self, table_name, cols):
        if self.cursor:
            cols = ', '.join([str(x) for x in cols])
            self.cursor.execute('create table if not exists ' + table_name + ' (' + cols + ')')
        else:
            self.logger.warning('Could not create table cursor is None! Table Name : ' + str(table_name))

    def drop_table(self, table_name):
        sql = 'DROP TABLE ' + table_name
        self.cursor.execute(sql)
        self.connection.commit()

    def update(self, table_name, cols, args, criteria=None):
        try:
            if self.connection:
                if criteria is None:
                    cols = ', '.join([str(x) for x in cols])
                    params = ', '.join(['?' for x in args])
                    sql = 'INSERT INTO ' + table_name + ' (' + cols + ') VALUES (' + params + ')'
                else:
                    update_list = ''
                    for index in range(len(cols)):
                        update_list = update_list + ' ' + cols[index] + ' = ?,'
                    update_list = update_list.strip(',')
                    sql = 'UPDATE ' + table_name + ' SET ' + update_list + ' where ' + criteria
                self.cursor.execute(sql, tuple(args))
                self.connection.commit()
            else:
                self.logger.warning('Could not update table cursor is None! Table Name : ' + str(table_name))
        except Exception as e:
            self.logger.error('Updating table error ! Table Name : ' + str(table_name) + ' ' + str(e))

    def delete(self, table_name, criteria):
        if self.cursor:
            sql = 'DELETE FROM ' + table_name
            if criteria:
                sql += ' where ' + str(criteria)
            self.cursor.execute(sql)
            self.connection.commit()

    def findByProperty(self):
        # Not implemented yet
        pass

    def select(self, table_name, cols='*', criteria='', orderby=''):
        if self.cursor:
            try:
                if not cols == '*':
                    cols = ', '.join([str(x) for x in cols])
                sql = 'SELECT ' + cols + ' FROM ' + table_name
                if criteria != '':
                    sql += ' where '
                    sql += criteria
                if orderby != '':
                    sql += ' order by '
                    sql += orderby

                self.cursor.execute(sql)

                rows = self.cursor.fetchall()
                return rows
            except Exception as e:
                raise
        else:
            self.logger.warning('Could not select table cursor is None! Table Name : ' + str(table_name))

    def select_one_result(self, table_name, col, criteria=''):
        if self.cursor:
            try:
                sql = 'SELECT ' + col + ' FROM ' + table_name
                if criteria != '':
                    sql += ' where '
                    sql += criteria
                self.cursor.execute(sql)
                row = self.cursor.fetchone()
                if row is not None:
                    return row[0]
                else:
                    return None
            except Exception as e:
                raise
        else:
            self.logger.warning('Could not select table cursor is None! Table Name : ' + str(table_name))

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            self.logger.error('Closing database connection error:' + str(e))
