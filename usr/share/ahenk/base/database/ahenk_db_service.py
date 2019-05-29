#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import sqlite3
import threading
from base.scope import Scope


class AhenkDbService(object):
    """
        Sqlite manager for ahenk
    """

    def __init__(self):
        scope = Scope.get_instance()
        self.logger = scope.get_logger()
        self.configurationManager = scope.get_configuration_manager()
        self.db_path = self.configurationManager.get('BASE', 'dbPath')
        self.connection = None
        self.cursor = None

        self.lock = threading.Lock()

        # TODO get columns anywhere
        # TODO scheduler db init get here

    def initialize_table(self):

        self.check_and_create_table('task',
                                    ['id INTEGER', 'create_date TEXT', 'modify_date TEXT', 'command_cls_id TEXT',
                                     'parameter_map BLOB', 'deleted INTEGER', 'plugin TEXT', 'cron_expr TEXT',
                                     'file_server TEXT'])
        self.check_and_create_table('policy',
                                    ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'type TEXT', 'version TEXT', 'name TEXT',
                                     'execution_id TEXT','expiration_date TEXT'])
        self.check_and_create_table('profile', ['id INTEGER', 'create_date TEXT', 'label TEXT', 'description TEXT',
                                                'overridable INTEGER', 'active TEXT', 'deleted TEXT',
                                                'profile_data TEXT', 'modify_date TEXT', 'plugin TEXT'])
        self.check_and_create_table('plugin',
                                    ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'active TEXT', 'create_date TEXT',
                                     'deleted TEXT', 'description TEXT', 'machine_oriented TEXT', 'modify_date TEXT',
                                     'name TEXT', 'policy_plugin TEXT', 'user_oriented TEXT', 'version TEXT',
                                     'task_plugin TEXT', 'x_based TEXT'])
        self.check_and_create_table('registration',
                                    ['jid TEXT', 'password TEXT', 'registered INTEGER', 'dn TEXT', 'params TEXT',
                                     'timestamp TEXT'])
        self.check_and_create_table('contract', ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'content BLOB', 'title TEXT',
                                                 'timestamp TEXT'])
        self.check_and_create_table('agreement',
                                    ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'contract_id TEXT', 'username TEXT',
                                     'timestamp TEXT', 'choice TEXT'])
        self.check_and_create_table('session', ['id INTEGER PRIMARY KEY AUTOINCREMENT','username TEXT', 'display TEXT', 'desktop TEXT', 'timestamp TEXT', 'ip TEXT'])

        self.check_and_create_table('mail', ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'command TEXT', 'mailstatus INTEGER',  'timestamp TEXT'])

        self.check_and_create_table('service', ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'serviceName TEXT', 'serviceStatus TEXT','timestamp TEXT','task_id INTEGER'])


    def get_cols(self, table_name):
        if table_name == 'agreement':
            return ['contract_id', 'username', 'timestamp', 'choice']
        elif table_name == 'contract':
            return ['content', 'title', 'timestamp']
        elif table_name == 'session':
            return ['username', 'display', 'desktop', 'timestamp', 'ip']
        elif table_name == 'task':
            return ['id', 'create_date', 'modify_date', 'command_cls_id', 'parameter_map', 'deleted', 'plugin',
                    'cron_expr', 'file_server']
        elif table_name == 'plugin':
            return ['id', 'active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date', 'name',
                    'policy_plugin', 'user_oriented', 'version', 'task_plugin', 'x_based']
        else:
            return None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.logger.error('Database connection error: {0}'.format(str(e)))

    def check_and_create_table(self, table_name, cols):

        try:
            self.lock.acquire(True)
            if self.cursor:
                cols = ', '.join([str(x) for x in cols])
                self.cursor.execute('create table if not exists ' + table_name + ' (' + cols + ')')
            else:
                self.logger.warning('Could not create table cursor is None! Table Name : {0}'.format(str(table_name)))
        finally:
            self.lock.release()

    def drop_table(self, table_name):
        try:
            self.lock.acquire(True)
            sql = 'DROP TABLE ' + table_name
            self.cursor.execute(sql)
            self.connection.commit()
        finally:
            self.lock.release()

    def update(self, table_name, cols, args, criteria=None):
        try:
            self.lock.acquire(True)
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
                return self.cursor.lastrowid
            else:
                self.logger.warning('Could not update table cursor is None! Table Name : {0}'.format(str(table_name)))
                return None
        except Exception as e:
            self.logger.error(
                'Updating table error ! Table Name : {0} Error Mesage: {1}'.format(str(table_name), str(e)))
        finally:
            self.lock.release()

    def delete(self, table_name, criteria):
        try:
            self.lock.acquire(True)
            if self.cursor:
                sql = 'DELETE FROM ' + table_name
                if criteria:
                    sql += ' where ' + str(criteria)
                self.cursor.execute(sql)
                self.connection.commit()
        finally:
            self.lock.release()

    def findByProperty(self):
        # Not implemented yet
        pass

    def select(self, table_name, cols='*', criteria='', orderby=''):
        if self.cursor:
            try:
                self.lock.acquire(True)
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
            except:
                raise
            finally:
                self.lock.release()
        else:
            self.logger.warning('Could not select table cursor is None! Table Name : {0}'.format(str(table_name)))

    def select_one_result(self, table_name, col, criteria=''):
        if self.cursor:
            try:
                self.lock.acquire(True)
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
            except:
                raise
            finally:
                self.lock.release()
        else:
            self.logger.warning('Could not select table cursor is None! Table Name : {0}'.format(str(table_name)))

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            self.logger.error('Closing database connection error: {0}'.format(str(e)))