#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import imp
import os

from base.Scope import Scope
from base.model.PluginBean import PluginBean
from base.model.PluginKillSignal import PluginKillSignal
from base.model.modes.init_mode import InitMode
from base.model.modes.login_mode import LoginMode
from base.model.modes.logout_mode import LogoutMode
from base.model.modes.safe_mode import SafeMode
from base.model.modes.shutdown_mode import ShutdownMode
from base.plugin.Plugin import Plugin
from base.plugin.PluginQueue import PluginQueue


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

        try:
            possible_plugins = os.listdir(self.configManager.get("PLUGIN", "pluginFolderPath"))
            self.logger.debug('[PluginManager] Possible plugins: {} '.format(str(possible_plugins)))
            for plugin_name in possible_plugins:
                location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), plugin_name)
                if not os.path.isdir(location) or not self.configManager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(location):
                    self.logger.debug('It is not a plugin location ! There is no main module - {}'.format(str(location)))
                    continue
                try:
                    self.loadSinglePlugin(plugin_name)
                except Exception as e:
                    self.logger.error('[PluginManager] Exception occurred when loading plugin ! Plugin name : {} .Error Message: {}'.format(str(plugin_name), str(e)))
            self.logger.info('[PluginManager] Loaded plugins successfully.')
        except Exception as e:
            self.logger.warning('[PluginManager] Plugin folder path not found. Error Message: {}'.format(str(e)))

    def loadSinglePlugin(self, plugin_name):
        # TODO check already loaded plugin
        self.pluginQueueDict[plugin_name] = PluginQueue()
        plugin = Plugin(plugin_name, self.pluginQueueDict[plugin_name])
        plugin.setDaemon(True)
        plugin.start()
        self.plugins.append(plugin)

        self.logger.debug('[PluginManager] New plugin was loaded. Plugin Name: {}'.format(plugin_name))

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
        self.messenger = scope.getMessenger()
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

    def is_profile_overridable(self, profiles, plugin_name):
        for profile in profiles:
            if profile.plugin.name == plugin_name and profile.overridable.lower() == 'true':
                return True
        return False

    def processPolicy(self, policy):

        self.logger.info('[PluginManager] Processing policies...')
        username = policy.username
        ahenk_profiles = policy.ahenk_profiles
        user_profiles = policy.user_profiles

        if ahenk_profiles is not None:
            self.logger.info('[PluginManager] Working on Ahenk profiles...')
            for agent_profile in ahenk_profiles:

                if agent_profile.overridable.lower() != 'true' and self.is_profile_overridable(policy.user_profiles, agent_profile.plugin.name) is True:
                    temp_list = []
                    self.logger.debug('[PluginManager] User profile of {0} plugin will not executed because of profile override rules.'.format(agent_profile.plugin.name))
                    for usr_profile in user_profiles:
                        if usr_profile.plugin.name != agent_profile.plugin.name:
                            temp_list.append(usr_profile)
                    user_profiles = temp_list
                else:
                    self.logger.debug('[PluginManager] Agent profile of {0} plugin will not executed because of profile override rules.'.format(agent_profile.plugin.name))
                    continue

                agent_profile.set_username(None)
                self.process_profile(agent_profile)

        if user_profiles is not None:
            self.logger.info('[PluginManager] Working on User profiles...')
            for user_profile in user_profiles:
                user_profile.set_username(username)
                self.process_profile(user_profile)

    def process_profile(self, profile):

        ##
        scope = Scope().getInstance()
        self.messenger = scope.getMessenger()
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

    def process_mode(self, mode_type, username=None):
        mode = None
        if mode_type == 'init':
            mode = InitMode()
        elif mode_type == 'shutdown':
            mode = ShutdownMode()
        elif mode_type == 'login':
            mode = LoginMode(username)
        elif mode_type == 'logout':
            mode = LogoutMode(username)
        elif mode_type == 'safe':
            mode = SafeMode(username)
        else:
            self.logger.error('[PluginManager] Unknown mode type: {}'.format(mode_type))

        if mode is not None:
            for plugin_name in self.pluginQueueDict:
                try:
                    self.pluginQueueDict[plugin_name].put(mode, 1)
                except Exception as e:
                    self.logger.error('[PluginManager] Exception occurred while switching safe mode. Error Message : {}'.format(str(e)))

    def find_module(self, mode, plugin_name):
        mode = mode.lower().replace('_mode', '')
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), plugin_name)

        if os.path.isdir(location) and (mode + ".py") in os.listdir(location):
            info = imp.find_module(mode, [location])
            return imp.load_module(mode, *info)
        else:
            self.logger.warning('[PluginManager] safe.py not found Plugin Name : ' + str(plugin_name))
            return None

    def reloadSinglePlugin(self, pluginName):
        # Not implemented yet

        pass

    def checkCommandExist(self, pluginName, commandId):
        # Not implemented yet
        pass

    def printQueueSize(self):
        print("size " + str(len(self.pluginQueueDict)))
