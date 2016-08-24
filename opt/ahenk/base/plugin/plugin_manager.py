#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import imp
import os

from base.scope import Scope
from base.model.plugin_bean import PluginBean
from base.model.modes.init_mode import InitMode
from base.model.modes.login_mode import LoginMode
from base.model.modes.logout_mode import LogoutMode
from base.model.modes.safe_mode import SafeMode
from base.model.modes.shutdown_mode import ShutdownMode
from base.plugin.Plugin import Plugin
from base.plugin.plugin_queue import PluginQueue
from base.plugin.plugin_install_listener import PluginInstallListener
from base.system.system import System


# TODO create base abstract class
class PluginManager(object):
    """docstring for PluginManager"""

    def __init__(self):
        super(PluginManager, self).__init__()
        self.scope = Scope.getInstance()
        self.configManager = self.scope.getConfigurationManager()
        self.db_service = self.scope.getDbService()
        self.message_manager = self.scope.getMessageManager()
        self.logger = self.scope.getLogger()

        self.plugins = []
        self.pluginQueueDict = dict()

        # self.listener = \
        self.install_listener()
        self.delayed_profiles = dict()
        self.delayed_tasks = dict()

    # TODO version?
    def load_plugins(self):
        self.logger.info('[PluginManager] Loading plugins...')
        self.plugins = []
        self.logger.debug('[PluginManager] Lookup for possible plugins...')
        try:
            possible_plugins = os.listdir(self.configManager.get("PLUGIN", "pluginFolderPath"))
            self.logger.debug('[PluginManager] Possible plugins: {0} '.format(str(possible_plugins)))
            for plugin_name in possible_plugins:
                try:
                    self.load_single_plugin(plugin_name)
                except Exception as e:
                    self.logger.error(
                        '[PluginManager] Exception occurred while loading plugin ! Plugin name : {0}.'
                        ' Error Message: {1}'.format(str(plugin_name), str(e)))
            self.logger.info('[PluginManager] Loaded plugins successfully.')
        except Exception as e:
            self.logger.warning('[PluginManager] Plugin folder path not found. Error Message: {0}'.format(str(e)))

    def load_single_plugin(self, plugin_name):
        # TODO check already loaded plugin
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), plugin_name)
        if not os.path.isdir(location) or not self.configManager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(
                location):
            self.logger.debug(
                '[PluginManager] It is not a plugin location ! There is no main module - {0}'.format(str(location)))
        else:
            if self.is_plugin_loaded(plugin_name):
                self.logger.debug(
                    '[PluginManager] {0} plugin was already loaded. Reloading {0} plugin'.format(plugin_name))
                # self.reload_single_plugin(plugin_name)
            else:
                self.pluginQueueDict[plugin_name] = PluginQueue()
                plugin = Plugin(plugin_name, self.pluginQueueDict[plugin_name])
                plugin.setDaemon(True)
                plugin.start()
                self.plugins.append(plugin)
                self.logger.debug('[PluginManager] New plugin was loaded. Plugin Name: {0}'.format(plugin_name))

                # active init mode
                mode = InitMode()
                self.pluginQueueDict[plugin_name].put(mode, 1)

        if plugin_name in self.delayed_profiles:
            self.pluginQueueDict[plugin_name].put(self.delayed_profiles[plugin_name], 1)
            del self.delayed_profiles[plugin_name]
            self.logger.debug('[PluginManager] Delayed profile was found for this plugin. It will be run.')
        if plugin_name in self.delayed_tasks:
            self.pluginQueueDict[plugin_name].put(self.delayed_tasks[plugin_name], 1)
            del self.delayed_tasks[plugin_name]
            self.logger.debug('[PluginManager] Delayed task was found for this plugin. It will be run.')

    def reload_plugins(self):
        try:
            self.logger.info('[PluginManager] Reloading plugins...')
            for p_queue in self.pluginQueueDict:
                self.pluginQueueDict[p_queue].put(ShutdownMode(), 1)
            self.plugins = []
            self.load_plugins()
            self.logger.info('[PluginManager] Plugin reloaded successfully.')
        except Exception as e:
            self.logger.error('[PluginManager] Exception occurred when reloading plugins ' + str(e))

    def reload_single_plugin(self, plugin_name):
        try:
            self.logger.info('[PluginManager] {0} plugin is reloading'.format(plugin_name))
            self.logger.debug('[PluginManager] {0} plugin is killing (in reloading action)'.format(plugin_name))
            self.remove_single_plugin(plugin_name)
            self.logger.debug('[PluginManager] {0} plugin is loading (in reloading action)'.format(plugin_name))
            self.load_single_plugin(plugin_name)
        except Exception as e:
            self.logger.error(
                '[PluginManager] A problem  occurred while reloading {0} plugin. Error Message: {1}'.format(plugin_name,
                                                                                                            str(e)))

    def remove_plugins(self):
        try:
            self.logger.debug('[PluginManager] Removing all plugins...')
            for p_queue in self.pluginQueueDict:
                self.pluginQueueDict[p_queue].put(ShutdownMode(), 1)
            self.plugins = []
            self.pluginQueueDict = dict()
            self.logger.debug('[PluginManager] All plugins were removed successfully.')
        except Exception as e:
            self.logger.error(
                '[PluginManager] A problem occurred while removing plugins. Error Message :{0}.'.format(str(e)))

    def remove_single_plugin(self, plugin_name):
        try:
            self.logger.debug('[PluginManager] Trying to remove {0} plugin...'.format(plugin_name))
            if self.is_plugin_loaded(plugin_name):
                self.logger.debug('[PluginManager] {0} plugin is killing...'.format(plugin_name))
                self.pluginQueueDict[plugin_name].put(ShutdownMode(), 1)
                del self.pluginQueueDict[plugin_name]

                for plugin in self.plugins:
                    if plugin.name == plugin_name:
                        self.plugins.remove(plugin)
                self.logger.debug('[PluginManager] {0} plugin was removed.'.format(plugin_name))
            else:
                self.logger.warning('[PluginManager] {0} plugin not found.'.format(plugin_name))
        except Exception as e:
            self.logger.error(
                '[PluginManager] A problem occurred while removing {0} plugin. Error Message :{1}.'.format(plugin_name,
                                                                                                           str(e)))

    def find_command(self, pluginName, commandId):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), pluginName)
        if os.path.isdir(location) and commandId + ".py" in os.listdir(location):
            info = imp.find_module(commandId, [location])
            return imp.load_module(commandId, *info)
        else:
            self.logger.warning('Command id -' + commandId + ' - not found')
            return None

    def process_task(self, task):

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
                self.logger.warning(
                    '[PluginManager] {0} plugin not found. Task was delayed. Ahenk will request plugin from Lider if distribution available'.format(
                        plugin_name))
                self.delayed_tasks[plugin_name] = task
                msg = self.message_manager.missing_plugin_message(PluginBean(name=plugin_name, version=plugin_ver))
                self.messenger.send_direct_message(msg)
        except Exception as e:
            self.logger.error(
                '[PluginManager] Exception occurred while processing task. Error Message: {0}'.format(str(e)))

    def find_policy_module(self, plugin_name):
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), plugin_name)
        if os.path.isdir(location) and "policy.py" in os.listdir(location):
            info = imp.find_module("policy", [location])
            return imp.load_module("policy", *info)
        else:
            self.logger.warning('[PluginManager] policy.py not found Plugin Name : ' + str(plugin_name))
            return None

    def process_policy(self, policy):

        self.logger.info('[PluginManager] Processing policies...')
        username = policy.username
        ahenk_profiles = policy.ahenk_profiles
        user_profiles = policy.user_profiles

        if ahenk_profiles is not None and len(ahenk_profiles) > 0:
            self.logger.info('[PluginManager] Working on Ahenk profiles...')
            for agent_profile in ahenk_profiles:
                same_plugin_profile = None

                if user_profiles is not None:
                    for usr_profile in user_profiles:
                        if usr_profile.plugin.name == agent_profile.plugin.name:
                            same_plugin_profile = usr_profile

                    if same_plugin_profile is not None:
                        if agent_profile.overridable.lower() == 'true':
                            self.logger.debug(
                                '[PluginManager] Agent profile of {0} plugin will not executed because of '
                                'profile override rules.'.format(agent_profile.plugin.name))
                            continue
                        else:
                            self.logger.warning(
                                '[PluginManager] User profile of {0} plugin will not executed because of '
                                'profile override rules.'.format(agent_profile.plugin.name))
                            user_profiles.remove(same_plugin_profile)

                agent_profile.set_username(None)
                self.process_profile(agent_profile)

        if user_profiles is not None and len(user_profiles) > 0:
            self.logger.info('[PluginManager] Working on User profiles...')
            for user_profile in user_profiles:
                user_profile.set_username(username)
                self.process_profile(user_profile)

    def process_profile(self, profile):

        try:
            plugin = profile.get_plugin()
            plugin_name = plugin.get_name()
            plugin_ver = plugin.get_version()
            if plugin_name in self.pluginQueueDict:
                self.pluginQueueDict[plugin_name].put(profile, 1)
            else:
                self.logger.warning(
                    '[PluginManager] {0} plugin not found. Profile was delayed. Ahenk will request plugin from Lider if distribution available'.format(
                        plugin_name))
                self.delayed_profiles[plugin_name] = profile
                msg = self.message_manager.missing_plugin_message(PluginBean(name=plugin_name, version=plugin_ver))
                self.scope.getMessenger().send_direct_message(msg)
        except Exception as e:
            self.logger.error(
                '[PluginManager] Exception occurred while processing profile. Error Message: {0}'.format(str(e)))

    def check_plugin_exists(self, plugin_name, version=None):

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
            self.logger.error('[PluginManager] Unknown mode type: {0}'.format(mode_type))

        if mode is not None:
            self.logger.info('[PluginManager] {0} mode is running'.format(mode_type))
            for plugin_name in self.pluginQueueDict:
                try:
                    self.pluginQueueDict[plugin_name].put(mode, 1)
                except Exception as e:
                    self.logger.error(
                        '[PluginManager] Exception occurred while switching safe mode. Error Message : {0}'.format(
                            str(e)))

    def find_module(self, mode, plugin_name):
        mode = mode.lower().replace('_mode', '')
        location = os.path.join(self.configManager.get("PLUGIN", "pluginFolderPath"), plugin_name)

        if os.path.isdir(location) and (mode + ".py") in os.listdir(location):
            info = imp.find_module(mode, [location])
            return imp.load_module(mode, *info)
        else:
            self.logger.warning('[PluginManager] {0} not found in {1} plugin'.format((mode + '.py'), plugin_name))
            return None

    def install_listener(self):
        listener = PluginInstallListener(System.Ahenk.plugins_path())
        listener.setDaemon(True)
        listener.start()

    def is_plugin_loaded(self, plugin_name):
        try:
            if self.pluginQueueDict[plugin_name] is not None:
                return True
            else:
                return False
        except Exception as e:
            return False

    def checkCommandExist(self, pluginName, commandId):
        # Not implemented yet
        pass

    def printQueueSize(self):
        print("size " + str(len(self.pluginQueueDict)))
