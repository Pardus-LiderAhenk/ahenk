#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.Scope import Scope

class TaskManager(object):
    """docstring for TaskManager"""
    def __init__(self):
        super(TaskManager, self).__init__()
        scope = Scope.getInstance()
        self.pluginManager = scope.getPluginManager()
        self.logger= scope.getLogger()

    def addTask(self,task):
        try:
            # TODO add log
            # TODO save task to database
            # TODO send task received message
            self.pluginManager.processTask(task)
        except Exception as e:
            # TODO error log here
            pass

    def saveTask(self,task):
        # TODO not implemented yet
        # task reveiced to ahenk save to db firstly.
        # if user close before processing task you can load from db for process
        pass

    def updateTask(self,task):
        # TODO not implemented yet
        # This is updates task status processing - processed ...
        pass

    def deleteTask(self,task):
        # TODO not implemented yet
        # remove task if it is processed
        pass
