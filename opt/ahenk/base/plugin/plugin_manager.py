#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import imp
import os

from base.Scope import Scope
from base.plugin.Plugin import Plugin
from base.plugin.PluginQueue import PluginQueue
from base.model.PluginKillSignal import PluginKillSignal

# TODO create base abstract class
class PluginManager(object):
    """docstring for PluginManager"""

    # implement logger
    def __init__(self):
        super(PluginManager, self).__init__()
        self.scope = Scope.getInstance()
        self.configManager = self.scope.getConfigurationManager()
        self.db_service = self.scope.getDbService()
        self.plugins = []
        self.pluginQueueDict = dict()
        self.logger = self.scope.getLogger()

    #TODO version?
    def loadPlugins(self):
        """
            This method loads plugins
        """
        self.logger.info('[PluginManager] Loading plugins...')
        self.plugins = []
        self.logger.debug('[PluginManager] Lookup for possible plugins...')
        possibleplugins = os.listdir(self.configManager.get("PLUGIN", "pluginFolderPath"))
        self.logger.debug('[PluginManager] Possible plugins.. ' + str(possibleplugins))
        for pname in possibleplugins:
            location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pname)
            if not os.path.isdir(location) or not self.configManager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(location):
                self.logger.debug('It is not a plugin location ! There is no main module - ' + str(location))
                continue
            try:
                self.loadSinglePlugin(pname)
            except Exception as e:
                self.logger.error('Exception occured when loading plugin ! Plugin name : ' + str(pname) + ' Exception : ' + str(e))
        self.logger.info('[PluginManager] Loaded plugins successfully.')

    def loadSinglePlugin(self, pluginName):
        # TODO check already loaded plugin
        self.pluginQueueDict[pluginName] = PluginQueue()
        plugin = Plugin(pluginName, self.pluginQueueDict[pluginName])
        plugin.setDaemon(True)
        plugin.start()
        self.plugins.append(plugin)

    def findCommand(self, pluginName, commandId):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pluginName)
        if os.path.isdir(location) and commandId + ".py" in os.listdir(location):
            info = imp.find_module(commandId, [location])
            return imp.load_module(commandId, *info)
        else:
            self.logger.warning('Command id -' + commandId + ' - not found')
            return None

    def processTask(self, task):
        try:
            if task.plugin.name.lower() in self.pluginQueueDict:
                self.pluginQueueDict[task.plugin.name.lower()].put(task, 1)
        except Exception as e:
            # TODO update task - status to not found command
            self.logger.error("[PluginManager] Exception occurred when processing task " + str(e))

    def reloadPlugins(self):
        #TODO
        try:
            self.logger.info('[PluginManager]  Reloading plugins... ')
            kill_sgnl = PluginKillSignal()
            for p_queue in self.pluginQueueDict:
                p_queue.put(kill_sgnl)
            self.plugins = []
            self.loadPlugins()
            self.logger.info('[PluginManager] Plugin reloaded successfully.')
        except Exception as e:
            self.logger.error('[PluginManager] Exception occurred when reloading plugins ' + str(e))

    def findPolicyModule(self, plugin_name):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), plugin_name)
        if os.path.isdir(location) and "policy.py" in os.listdir(location):
            info = imp.find_module("policy", [location])
            return imp.load_module("policy", *info)
        else:
            self.logger.warning('[PluginManager] policy.py not found Plugin Name : ' + str(plugin_name))
            return None

    def processPolicy(self, policy):
        #TODO do you need username in profile?

        username = policy.username
        ahenk_profiles = policy.ahenk_profiles
        user_profiles = policy.user_profiles

        if ahenk_profiles is not None:
            for profile in ahenk_profiles:
                self.process_profile(profile)

        if user_profiles is not None:
            for profile in user_profiles:
                profile.set_username(username)
                self.process_profile(profile)

    def process_profile(self, profile):
        try:
            plugin = profile.get_plugin()
            plugin_name = plugin.name
            if plugin_name in self.pluginQueueDict:
                self.pluginQueueDict[plugin_name].put(profile, 1)
        except Exception as e:
            print("Exception occured..")
            self.logger.error("Policy profile not processed " + str(profile.plugin.name))

    def checkPluginExists(self, plugin_name, version=None):

        criteria = ' name=\''+plugin_name+'\''
        if version is not None:
            criteria += ' and version=\'' + str(version) + '\''
        result = self.db_service.select('plugin', 'name', criteria)

        if result is None:
            return False
        else:
            return True

    def reloadSinglePlugin(self, pluginName):
        # Not implemented yet

        pass

    def checkCommandExist(self, pluginName, commandId):
        # Not implemented yet
        pass

    def printQueueSize(self):
        print("size " + str(len(self.pluginQueueDict)))

