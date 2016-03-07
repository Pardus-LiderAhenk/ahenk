#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.Scope import Scope
import sqlite3

class AhenkDbService(object):
    """
        Sqlite manager for ahenk
    """
    def __init__(self):
        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        self.db_path=self.configurationManager.get("BASE","dbPath")
        self.connection=None
        self.cursor = None

    def connect():
        try:
            self.connection=sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.logger.error('Database connection error ' + str(e))

    def check_and_create_table(self,table_name,cols):
        if self.cursor:
            cols = ', '.join([str(x) for x in cols])
            self.cursor.execute("create table if not exists "+table_name+" ("+cols+")")
        else
            self.warn("Could not create table cursor is None! Table Name : " + str(table_name))

    def update(self, table_name, cols, args, criteria=None):
        try:
            if self.connection:
                if criteria == None:
                    cols = ', '.join([str(x) for x in cols])
                    params = ', '.join(["?" for x in args])
                    sql = "INSERT INTO "+table_name+" ("+cols+") VALUES ("+params+")"
                    self.cursor.execute(sql, tuple(args))
                else:
                    update_list = ""
                    params = ', '.join(["?" for x in args])
                    for index in range(len(cols)):
                        update_list = update_list + " " + cols[index] +" = ?,"

                    update_list = update_list.strip(',')
                    sql = "UPDATE "+table_name+" SET " + update_list  + " " +  criteria
                    self.cursor.execute(sql, tuple(args))
                self.connection.commit()
            else:
                self.warn("Could not update table cursor is None! Table Name : " + str(table_name))
        except Exception, e:
            self.logger.error("Updating table error ! Table Name : " + str(table_name) + " " + str(e))

    def delete(self):
        sql = "DELETE FROM " + table_name + str(criteria)
        self.cursor.execute(sql)
        self.connection.commit()

    def findByProperty(self):
        # Not implemented yet
        pass
    def select(self,table_name, cols="*",  criteria="", orderby=""):
        if self.cursor:
            try:
                if not cols == "*":
                    cols = ', '.join([str(x) for x in cols])
                sql = "SELECT "+cols+" FROM " + table_name  + " " + str(criteria)  + " " +  orderby
                self.cursor.execute(sql)
                rows = self.cursor.fetchall()
                return rows
            except Exception as e:
                raise
        else:
            self.warn("Could not select table cursor is None! Table Name : " + str(table_name))

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
        except Exception as e:
            self.logger.error("Closing database connection error " + str(e)) 
