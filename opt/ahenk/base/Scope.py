#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>


class Scope(object):
    """docstring for Scope"""

    scopeInstance=None

    def __init__(self):
        super(Scope, self).__init__()
        self.customMap = {}
        self.configurationManager=None
        self.messageManager=None
        self.logger=None
        self.pluginManager=None
        self.taskManager=None
        self.responseQueue=None

    @staticmethod
    def getInstance():
        return scopeInstance

    @staticmethod
    def setInstance(scopeObj):
        global scopeInstance
        scopeInstance = scopeObj

    def getCustomMap(self):
        return self.customMap

    def putCustomMap(self,name,value):
        self.custom[str(name)]=value

    def getCustomParam(self,name):
        return self.customMap[str(name)]

    def getConfigurationManager(self):
        return self.configurationManager

    def setConfigurationManager(self,configurationManager):
        self.configurationManager = configurationManager

    def getLogger(self):
        return self.logger

    def setLogger(self,logger):
        self.logger = logger

    def getMessageManager(self):
        return self.messageManager

    def setMessageManager(self,messageManager):
        self.messageManager = messageManager

    def getPluginManager(self):
        return self.pluginManager

    def setPluginManager(self,pluginManager):
        self.pluginManager = pluginManager

    def getTaskManager(self):
        return self.TaskManager

    def setTaskManager(self,taskManager):
        self.taskManager = taskManager

    def getResponseQueue(self):
        return self.responseQueue

    def setResponseQueue(self,responseQueue):
        self.responseQueue=responseQueue
