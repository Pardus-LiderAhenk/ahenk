#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import imp
import os

from base.Scope import Scope
from base.plugin.Plugin import Plugin
from base.plugin.PluginQueue import PluginQueue
from base.model.PluginKillSignal import PluginKillSignal
from base.model.PluginBean import PluginBean


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
        self.message_manager = self.scope.getMessageManager()
        self.delayed_profiles = {}
        self.delayed_tasks = {}

    # TODO version?
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
                self.logger.error('[PluginManager] Exception occured when loading plugin ! Plugin name : ' + str(pname) + ' Exception : ' + str(e))
        self.logger.info('[PluginManager] Loaded plugins successfully.')

    def loadSinglePlugin(self, plugin_name):
        # TODO check already loaded plugin
        self.pluginQueueDict[plugin_name] = PluginQueue()
        plugin = Plugin(plugin_name, self.pluginQueueDict[plugin_name])
        plugin.setDaemon(True)
        plugin.start()
        self.plugins.append(plugin)

        self.logger.debug('[PluginManager] New plugin was loaded.')

        if len(self.delayed_profiles) > 0:
            self.pluginQueueDict[plugin_name].put(self.delayed_profiles[plugin_name], 1)
            self.logger.debug('[PluginManager] Delayed profile was found for this plugin. It will be run.')
        if len(self.delayed_tasks) > 0:
            self.pluginQueueDict[plugin_name].put(self.delayed_tasks[plugin_name], 1)
            self.logger.debug('[PluginManager] Delayed task was found for this plugin. It will be run.')

    def findCommand(self, pluginName, commandId):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pluginName)
        if os.path.isdir(location) and commandId + ".py" in os.listdir(location):
            info = imp.find_module(commandId, [location])
            return imp.load_module(commandId, *info)
        else:
            self.logger.warning('Command id -' + commandId + ' - not found')
            return None

    def processTask(self, task):

        ##
        scope = Scope().getInstance()
        self.messenger = scope.getMessager()
        ##

        try:
            plugin_name = task.get_plugin().get_name().lower()
            plugin_ver = task.get_plugin().get_version()
            if plugin_name in self.pluginQueueDict:
                self.pluginQueueDict[plugin_name].put(task, 1)
            else:
                self.logger.warning('[PluginManager] {} plugin not found. Task was delayed. Ahenk will request plugin from Lider if distribution available'.format(plugin_name))
                self.delayed_tasks[plugin_name] = task
                msg = self.message_manager.missing_plugin_message(PluginBean(name=plugin_name, version=plugin_ver))
                self.messenger.send_direct_message(msg)
        except Exception as e:
            self.logger.error('[PluginManager] Exception occurred while processing task. Error Message: {}'.format(str(e)))

    def reloadPlugins(self):
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

        self.logger.info('[PluginManager] Processing policies...')
        username = policy.username
        ahenk_profiles = policy.ahenk_profiles
        user_profiles = policy.user_profiles

        if ahenk_profiles is not None:
            self.logger.info('[PluginManager] Working on Ahenk profiles...')
            for profile in ahenk_profiles:
                profile.set_username(None)
                self.process_profile(profile)

        if user_profiles is not None:
            self.logger.info('[PluginManager] Working on User profiles...')
            for profile in user_profiles:
                profile.set_username(username)
                self.process_profile(profile)

    def process_profile(self, profile):

        ##
        scope = Scope().getInstance()
        self.messenger = scope.getMessager()
        ##
        try:
            plugin = profile.get_plugin()
            plugin_name = plugin.get_name()
            plugin_ver = plugin.get_version()
            if plugin_name in self.pluginQueueDict:
                self.pluginQueueDict[plugin_name].put(profile, 1)
            else:
                self.logger.warning('[PluginManager] {} plugin not found. Profile was delayed. Ahenk will request plugin from Lider if distribution available'.format(plugin_name))
                self.delayed_profiles[plugin_name] = profile
                msg = self.message_manager.missing_plugin_message(PluginBean(name=plugin_name, version=plugin_ver))
                self.messenger.send_direct_message(msg)
        except Exception as e:
            self.logger.error('[PluginManager] Exception occurred while processing profile. Error Message: {}'.format(str(e)))

    def checkPluginExists(self, plugin_name, version=None):

        criteria = ' name=\'' + plugin_name + '\''
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
