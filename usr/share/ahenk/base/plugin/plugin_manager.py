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
from base.plugin.plugin import Plugin
from base.plugin.plugin_queue import PluginQueue
from base.plugin.plugin_install_listener import PluginInstallListener
from base.system.system import System


# TODO create base abstract class
class PluginManager(object):
    """docstring for PluginManager"""

    def __init__(self):
        super(PluginManager, self).__init__()
        self.scope = Scope.get_instance()
        self.config_manager = self.scope.get_configuration_manager()
        self.db_service = self.scope.get_db_service()
        self.message_manager = self.scope.get_message_manager()
        self.logger = self.scope.get_logger()

        self.plugins = []
        self.plugin_queue_dict = dict()

        # self.listener = \
        self.install_listener()
        self.delayed_profiles = dict()
        self.delayed_tasks = dict()

    # TODO version?
    def load_plugins(self):
        self.logger.info('Loading plugins...')
        self.plugins = []
        self.logger.debug('Lookup for possible plugins...')
        try:
            possible_plugins = os.listdir(self.config_manager.get("PLUGIN", "pluginFolderPath"))
            self.logger.debug('Possible plugins: {0} '.format(str(possible_plugins)))
            for plugin_name in possible_plugins:
                try:
                    self.load_single_plugin(plugin_name)
                except Exception as e:
                    self.logger.error(
                        'Exception occurred while loading plugin ! Plugin name : {0}.'
                        ' Error Message: {1}'.format(str(plugin_name), str(e)))
            self.logger.info('Loaded plugins successfully.')
        except Exception as e:
            self.logger.warning('Plugin folder path not found. Error Message: {0}'.format(str(e)))

    def load_single_plugin(self, plugin_name):
        # TODO check already loaded plugin
        location = os.path.join(self.config_manager.get("PLUGIN", "pluginFolderPath"), plugin_name)
        if not os.path.isdir(location) or not self.config_manager.get("PLUGIN", "mainModuleName") + ".py" in os.listdir(
                location):
            self.logger.debug(
                'It is not a plugin location ! There is no main module - {0}'.format(str(location)))
        else:
            if self.is_plugin_loaded(plugin_name):
                self.logger.debug(
                    '{0} plugin was already loaded. Reloading {0} plugin'.format(plugin_name))
                # self.reload_single_plugin(plugin_name)
            else:
                self.plugin_queue_dict[plugin_name] = PluginQueue()
                plugin = Plugin(plugin_name, self.plugin_queue_dict[plugin_name])
                plugin.setDaemon(True)
                plugin.start()
                self.plugins.append(plugin)
                self.logger.debug('New plugin was loaded. Plugin Name: {0}'.format(plugin_name))

                # active init mode
                mode = InitMode()
                self.plugin_queue_dict[plugin_name].put(mode, 1)

        if plugin_name in self.delayed_profiles:
            self.plugin_queue_dict[plugin_name].put(self.delayed_profiles[plugin_name], 1)
            del self.delayed_profiles[plugin_name]
            self.logger.debug('Delayed profile was found for this plugin. It will be run.')
        if plugin_name in self.delayed_tasks:
            self.plugin_queue_dict[plugin_name].put(self.delayed_tasks[plugin_name], 1)
            del self.delayed_tasks[plugin_name]
            self.logger.debug('Delayed task was found for this plugin. It will be run.')

    def reload_plugins(self):
        try:
            self.logger.info('Reloading plugins...')
            for p_queue in self.plugin_queue_dict:
                self.plugin_queue_dict[p_queue].put(ShutdownMode(), 1)
            self.plugins = []
            self.load_plugins()
            self.logger.info('Plugin reloaded successfully.')
        except Exception as e:
            self.logger.error('Exception occurred when reloading plugins ' + str(e))

    def reload_single_plugin(self, plugin_name):
        try:
            self.logger.info('{0} plugin is reloading'.format(plugin_name))
            self.logger.debug('{0} plugin is killing (in reloading action)'.format(plugin_name))
            self.remove_single_plugin(plugin_name)
            self.logger.debug('{0} plugin is loading (in reloading action)'.format(plugin_name))
            self.load_single_plugin(plugin_name)
        except Exception as e:
            self.logger.error(
                'A problem  occurred while reloading {0} plugin. Error Message: {1}'.format(plugin_name,
                                                                                            str(e)))

    def remove_plugins(self):
        try:
            self.logger.debug('Removing all plugins...')
            for p_queue in self.plugin_queue_dict:
                self.plugin_queue_dict[p_queue].put(ShutdownMode(), 1)
            self.plugins = []
            self.plugin_queue_dict = dict()
            self.logger.debug('All plugins were removed successfully.')
        except Exception as e:
            self.logger.error(
                'A problem occurred while removing plugins. Error Message :{0}.'.format(str(e)))

    def remove_single_plugin(self, plugin_name):
        try:
            self.logger.debug('Trying to remove {0} plugin...'.format(plugin_name))
            if self.is_plugin_loaded(plugin_name):
                self.logger.debug('{0} plugin is killing...'.format(plugin_name))
                self.plugin_queue_dict[plugin_name].put(ShutdownMode(), 1)
                del self.plugin_queue_dict[plugin_name]

                for plugin in self.plugins:
                    if plugin.name == plugin_name:
                        self.plugins.remove(plugin)
                self.logger.debug('{0} plugin was removed.'.format(plugin_name))
            else:
                self.logger.warning('{0} plugin not found.'.format(plugin_name))
        except Exception as e:
            self.logger.error(
                'A problem occurred while removing {0} plugin. Error Message :{1}.'.format(plugin_name,
                                                                                           str(e)))

    def find_command(self, plugin_name, version, command_id):
        location = os.path.join(self.config_manager.get("PLUGIN", "pluginFolderPath"), plugin_name)
        if os.path.isdir(location) and command_id + ".py" in os.listdir(location):
            info = imp.find_module(command_id, [location])
            return imp.load_module(command_id, *info)
        else:
            self.logger.warning('Command id -' + command_id + ' - not found')
            return None

    def process_task(self, task):

        ##
        scope = Scope().get_instance()
        self.messenger = scope.get_messenger()
        ##

        try:
            plugin_name = task.get_plugin().get_name().lower()
            plugin_ver = task.get_plugin().get_version()

            if self.does_plugin_exist(plugin_name, plugin_ver) and plugin_name in self.plugin_queue_dict:
                self.plugin_queue_dict[plugin_name].put(task, 1)
            else:
                self.logger.warning(
                    '{0} plugin not found. Task was delayed. Ahenk will request plugin from Lider if distribution available'.format(
                        plugin_name, plugin_ver))
                self.delayed_tasks[plugin_name] = task
                msg = self.message_manager.missing_plugin_message(PluginBean(name=plugin_name, version=plugin_ver))
                self.messenger.send_direct_message(msg)
        except Exception as e:
            self.logger.error(
                'Exception occurred while processing task. Error Message: {0}'.format(str(e)))

    def find_policy_module(self, plugin_name):
        location = os.path.join(self.config_manager.get("PLUGIN", "pluginFolderPath"), plugin_name)
        if os.path.isdir(location) and "policy.py" in os.listdir(location):
            info = imp.find_module("policy", [location])
            return imp.load_module("policy", *info)
        else:
            self.logger.warning('policy.py not found Plugin Name : ' + str(plugin_name))
            return None

    def process_policy(self, policy):

        self.logger.info('Processing policies...')
        username = policy.username
        ahenk_profiles = policy.ahenk_profiles
        user_profiles = policy.user_profiles

        if ahenk_profiles is not None and len(ahenk_profiles) > 0:
            self.logger.info('Working on Ahenk profiles...')
            for agent_profile in ahenk_profiles:
                same_plugin_profile = None

                if user_profiles is not None:
                    for usr_profile in user_profiles:
                        if usr_profile.plugin.name == agent_profile.plugin.name:
                            same_plugin_profile = usr_profile

                    if same_plugin_profile is not None:
                        if agent_profile.overridable.lower() == 'true':
                            self.logger.debug(
                                'Agent profile of {0} plugin will not executed because of '
                                'profile override rules.'.format(agent_profile.plugin.name))
                            continue
                        else:
                            self.logger.warning(
                                'User profile of {0} plugin will not executed because of '
                                'profile override rules.'.format(agent_profile.plugin.name))
                            user_profiles.remove(same_plugin_profile)

                agent_profile.set_username(None)
                self.process_profile(agent_profile)

        if user_profiles is not None and len(user_profiles) > 0:
            self.logger.info('Working on User profiles...')
            for user_profile in user_profiles:
                user_profile.set_username(username)
                self.process_profile(user_profile)

    def process_profile(self, profile):

        try:
            plugin = profile.get_plugin()
            plugin_name = plugin.get_name()
            plugin_ver = plugin.get_version()
            if self.does_plugin_exist(plugin_name, plugin_ver) and plugin_name in self.plugin_queue_dict:
                self.plugin_queue_dict[plugin_name].put(profile, 1)
            else:
                self.logger.warning(
                    '{0} plugin  {1} version not found. Profile was delayed. Ahenk will request plugin from Lider if distribution available'.format(
                        plugin_name, plugin_ver))
                self.delayed_profiles[plugin_name] = profile
                msg = self.message_manager.missing_plugin_message(PluginBean(name=plugin_name, version=plugin_ver))
                self.scope.get_messenger().send_direct_message(msg)
        except Exception as e:
            self.logger.error(
                'Exception occurred while processing profile. Error Message: {0}'.format(str(e)))

    def does_plugin_exist(self, name, version):
        location = os.path.join(self.config_manager.get("PLUGIN", "pluginFolderPath"), name)
        main = self.config_manager.get("PLUGIN", "mainModuleName")
        if os.path.isdir(location) and main + ".py" in os.listdir(location):
            info = imp.find_module(main, [location])
            main_py = imp.load_module(main, *info)
            if main_py.info() is None or main_py.info()['version'] == version:
                return True
        return False

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
            self.logger.error('Unknown mode type: {0}'.format(mode_type))

        if mode is not None:
            self.logger.info('{0} mode is running'.format(mode_type))
            for plugin_name in self.plugin_queue_dict:
                try:
                    self.plugin_queue_dict[plugin_name].put(mode, 1)
                except Exception as e:
                    self.logger.error(
                        'Exception occurred while switching safe mode. Error Message : {0}'.format(
                            str(e)))

    def find_module(self, mode, plugin_name):
        mode = mode.lower().replace('_mode', '')
        location = os.path.join(self.config_manager.get("PLUGIN", "pluginFolderPath"), plugin_name)

        if os.path.isdir(location) and (mode + ".py") in os.listdir(location):
            info = imp.find_module(mode, [location])
            return imp.load_module(mode, *info)
        else:
            self.logger.warning('{0} not found in {1} plugin'.format((mode + '.py'), plugin_name))
            return None

    def install_listener(self):
        listener = PluginInstallListener(System.Ahenk.plugins_path())
        listener.setDaemon(True)
        listener.start()

    def is_plugin_loaded(self, plugin_name):
        try:
            if self.plugin_queue_dict[plugin_name] is not None:
                return True
            else:
                return False
        except Exception as e:
            return False

    def checkCommandExist(self, pluginName, commandId):
        # Not implemented yet
        pass

    def printQueueSize(self):
        print("size " + str(len(self.plugin_queue_dict)))
