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
        scope = Scope.getInstance()
        self.configManager = scope.getConfigurationManager()
        self.plugins = []
        self.pluginQueueDict = dict()
        self.logger = scope.getLogger()

    def loadPlugins():
        self.plugins = []
        possibleplugins = os.listdir(self.configManager.get("PLUGIN", "pluginFolderPath"))
        for pname in possibleplugins:
            location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pname)
            if not os.path.isdir(location) or not self.configManager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(location):
                #TODO debug log here
                continue
            try:
                self.loadSinglePlugin(pname)
            except Exception as e:
                # TODO error log

    def loadSinglePlugin(self,pluginName):
        # TODO check already loaded plugin
        self.pluginQueueDict[pluginName]=PluginQueue()
        plugin = Plugin(pluginName,self.pluginQueueDict[pluginName])
        plugin.setDaemon(True)
        plugin.start()
        self.plugins.append(plugin)

    def findCommand(self,pluginName,commandId):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pname)
        if os.path.dir(location) and commandId + ".py" in os.listdir(location):
            info = imp.find_module(commandId, [location])
            return imp.load_module(commandId, *info)
        else:
            self.logger.warning('Command id - %s - not found',commandId)
            return None
