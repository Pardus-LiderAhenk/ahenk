#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.plugin.Plugin import Plugin
from base.plugin.PluginQueue import PluginQueue
from base.Scope import Scope
import imp,os

class PluginManager(object):
    """docstring for PluginManager"""
    #implement logger
    def __init__(self):
        super(PluginManager, self).__init__()
        self.scope = Scope.getInstance()
        self.configManager = self.scope.getConfigurationManager()
        self.plugins = []
        self.pluginQueueDict = dict()
        self.logger = self.scope.getLogger()

    def loadPlugins(self):
        self.plugins = []
        possibleplugins = os.listdir(self.configManager.get("PLUGIN", "pluginFolderPath"))
        for pname in possibleplugins:
            location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pname)
            if not os.path.isdir(location) or not self.configManager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(location):
                self.logger.debug('It is not a plugin location - - ')
                continue
            try:
                self.loadSinglePlugin(pname)
            except Exception as e:
                # TODO error log
                pass

    def loadSinglePlugin(self,pluginName):
        # TODO check already loaded plugin
        self.pluginQueueDict[pluginName]=PluginQueue()
        plugin = Plugin(pluginName,self.pluginQueueDict[pluginName])
        plugin.setDaemon(True)
        plugin.start()
        self.plugins.append(plugin)

    def findCommand(self,pluginName,commandId):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pluginName)
        if os.path.isdir(location) and commandId + ".py" in os.listdir(location):
            info = imp.find_module(commandId, [location])
            return imp.load_module(commandId, *info)
        else:
            self.logger.warning('Command id -' +  commandId  +' - not found')
            return None

    def processTask(self,task):
        try:
            if task.plugin.name.lower() in self.pluginQueueDict :
                self.pluginQueueDict[task.plugin.name.lower()].put(task,1)
        except Exception as e:
            # TODO update task - status to not found command
            self.logger.error("[PluginManager] Exception occurred when processing task " + str(e))


    def reloadPlugins(self):
        # Not implemented yet
        pass

    def checkPluginExists(self,pluginName):
        # Not implemented yet
        pass

    def reloadSinglePlugin(self,pluginName):
        # Not implemented yet
        pass

    def checkCommandExist(self,pluginName,commandId):
        # Not implemented yet
        pass

    def printQueueSize(self):
        print("size " + str(len(self.pluginQueueDict)))
