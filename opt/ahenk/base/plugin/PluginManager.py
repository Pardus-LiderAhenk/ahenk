#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.plugin.Plugin import Plugin
import imp,os

class PluginManager(object):
    """docstring for PluginManager"""
    #implement logger
    def __init__(self, configManager):
        super(PluginManager, self).__init__()
        self.configManager = configManager
        self.plugins = []

    def loadPlugins():
        self.plugins = []
        possibleplugins = os.listdir(self.configManager.get("PLUGIN", "pluginFolderPath"))
        for pname in possibleplugins:
            location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pname)
            if not os.path.isdir(location) or not self.configManager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(location):
                continue
            info = imp.find_module(self.configManager.get("PLUGIN", "mainModuleName"), [location])
            mainModule = self.loadSinglePlugin(info):
            self.plugins.append(Plugin(pname,mainModule))

    def loadSinglePlugin(pluginInfo):
        return imp.load_module(self.configManager.get("PLUGIN", "mainModuleName"), pluginInfo)

    def findSinglePlugin(pluginName):
        pass # Not implemented yet
