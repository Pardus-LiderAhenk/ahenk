#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import hashlib
import json
import os
import shutil
import stat
import subprocess
import uuid
import urllib.request
import errno

from base.Scope import Scope
from base.messaging.ssh_file_transfer import FileTransfer
from base.model.PluginBean import PluginBean
from base.model.PolicyBean import PolicyBean
from base.model.ProfileBean import ProfileBean
from base.model.TaskBean import TaskBean
from base.model.enum.MessageType import MessageType


class ExecutionManager(object):
    """docstring for FileTransferManager"""

    def __init__(self):
        super(ExecutionManager, self).__init__()

        scope = Scope.getInstance()
        self.config_manager = scope.getConfigurationManager()
        self.event_manager = scope.getEventManager()
        self.task_manager = scope.getTaskManager()
        self.messenger = scope.getMessager()
        self.logger = scope.getLogger()
        self.db_service = scope.getDbService()
        self.message_manager = scope.getMessageManager()
        self.plugin_manager = scope.getPluginManager()

        self.event_manager.register_event(MessageType.EXECUTE_SCRIPT.value, self.execute_script)
        # send file ahenk to lider
        self.event_manager.register_event(MessageType.REQUEST_FILE.value, self.request_file)
        # send file lider to ahenk
        self.event_manager.register_event(MessageType.RETRIVE_FILE.value, self.retrive_file)
        self.event_manager.register_event(MessageType.MOVE_FILE.value, self.move_file)
        self.event_manager.register_event(MessageType.EXECUTE_TASK.value, self.execute_task)
        self.event_manager.register_event(MessageType.EXECUTE_POLICY.value, self.execute_policy)
        self.event_manager.register_event(MessageType.INSTALL_PLUGIN.value, self.install_plugin)

    def install_plugin(self, arg):
        plugin = json.loads(arg)
        self.logger.debug('[ExecutionManager] Installing missing plugin')
        try:
            plugin_name = plugin['pluginName']
            plugin_version = plugin['pluginVersion']
            parameter_map = json.loads(json.dumps(plugin['parameterMap']))

            temp_file = self.config_manager.get('CONNECTION', 'receivefileparam') + str(uuid.uuid4()) + '.deb'

            if str(plugin['protocol']).lower() == 'ssh':
                try:
                    self.logger.debug('[ExecutionManager] Distribution protocol is {}'.format(str(plugin['protocol']).lower()))
                    host = parameter_map['host']
                    username = parameter_map['username']
                    password = parameter_map['password']
                    port = parameter_map['port']
                    path = parameter_map['path']

                    transfer = FileTransfer(host, port, username, password)
                    transfer.connect()
                    transfer.get_file(temp_file, path)
                except Exception as e:
                    self.logger.error('[ExecutionManager] Plugin package could not fetch. Error Message: {}.'.format(str(e)))
                    self.logger.error('[ExecutionManager] Plugin Installation is cancelling')
                    return

            elif plugin['protocol'].lower() == 'http':
                self.logger.debug('[ExecutionManager] Distribution protocol is {}.'.format(str(plugin['protocol']).lower()))
                urllib.request.urlretrieve(parameter_map['url'], temp_file)
            else:
                self.logger.debug('[ExecutionManager] Unsupported protocol is {}.'.format(str(plugin['protocol']).lower()))

            self.logger.debug('[ExecutionManager] Plugin package downloaded via {}.'.format(str(plugin['protocol']).lower()))
            try:
                self.install_deb(temp_file)
                self.logger.debug('[ExecutionManager] Plugin installed.')
            except Exception as e:
                self.logger.error('[ExecutionManager] Could not install plugin. Error Message: {}'.format(str(e)))
                return

            try:
                self.remove_file(temp_file)
                self.logger.debug('[ExecutionManager] Temp files were removed.')
            except Exception as e:
                self.logger.error('[ExecutionManager] Could not remove temp file. Error Message: {}'.format(str(e)))

            self.plugin_manager.loadSinglePlugin(plugin_name)

        except Exception as e:
            self.logger.error('[ExecutionManager] A problem occurred while installing new ahenk plugin. Error Message:{}'.format(str(e)))

    def execute_policy(self, arg):

        ##
        scope = Scope().getInstance()
        self.messenger = scope.getMessager()
        ##

        self.logger.debug('[ExecutionManager] Updating policies...')
        policy = self.json_to_PolicyBean(json.loads(arg))
        machine_uid = self.db_service.select_one_result('registration', 'jid', 'registered=1')
        ahenk_policy_ver = self.db_service.select_one_result('policy', 'version', 'type = \'A\'')
        user_policy_version = self.db_service.select_one_result('policy', 'version', 'type = \'U\' and name = \'' + policy.get_username() + '\'')

        profile_columns = ['id', 'create_date', 'modify_date', 'label', 'description', 'overridable', 'active', 'deleted', 'profile_data', 'plugin']
        plugin_columns = ['active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date', 'name', 'policy_plugin', 'user_oriented', 'version']

        if policy.get_ahenk_policy_version() != ahenk_policy_ver:
            ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')
            if ahenk_policy_id is not None:
                self.db_service.delete('profile', 'id=' + str(ahenk_policy_id))
                self.db_service.delete('plugin', 'id=' + str(ahenk_policy_id))
                self.db_service.update('policy', ['version'], [str(policy.get_ahenk_policy_version())], 'type=\'A\'')
            else:
                self.db_service.update('policy', ['type', 'version', 'name', 'execution_id'], ['A', str(policy.get_ahenk_policy_version()), machine_uid, policy.get_agent_execution_id()])
                ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')

            for profile in policy.get_ahenk_profiles():
                plugin = profile.get_plugin()

                plugin_args = [str(plugin.get_active()), str(plugin.get_create_date()), str(plugin.get_deleted()), str(plugin.get_description()), str(plugin.get_machine_oriented()), str(plugin.get_modify_date()), str(plugin.get_name()), str(plugin.get_policy_plugin()), str(plugin.get_user_oriented()), str(plugin.get_version())]
                plugin_id = self.db_service.update('plugin', plugin_columns, plugin_args)

                profile_args = [str(ahenk_policy_id), str(profile.get_create_date()), str(profile.get_modify_date()), str(profile.get_label()), str(profile.get_description()), str(profile.get_overridable()), str(profile.get_active()), str(profile.get_deleted()), str(profile.get_profile_data()), plugin_id]
                self.db_service.update('profile', profile_columns, profile_args)

        else:
            self.logger.debug('[ExecutionManager] Already there is ahenk policy')

        if policy.get_user_policy_version() != user_policy_version:
            user_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'U\' and name=\'' + policy.get_username() + '\'')
            if user_policy_id is not None:
                # TODO remove profiles' plugins
                self.db_service.delete('profile', 'id=' + str(user_policy_id))
                self.db_service.delete('plugin', 'id=' + str(user_policy_id))
                self.db_service.update('policy', ['version'], [str(policy.get_user_policy_version())], 'type=\'U\' and name=\'' + policy.get_username() + '\'')
            else:
                self.db_service.update('policy', ['type', 'version', 'name', 'execution_id'], ['U', str(policy.get_user_policy_version()), policy.get_username(), policy.get_user_execution_id()])
                user_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'U\' and name=\'' + policy.get_username() + '\'')

            for profile in policy.get_user_profiles():
                plugin = profile.get_plugin()

                plugin_args = [str(plugin.get_active()), str(plugin.get_create_date()), str(plugin.get_deleted()), str(plugin.get_description()), str(plugin.get_machine_oriented()), str(plugin.get_modify_date()), str(plugin.get_name()), str(plugin.get_policy_plugin()), str(plugin.get_user_oriented()), str(plugin.get_version())]
                plugin_id = self.db_service.update('plugin', plugin_columns, plugin_args)

                profile_args = [str(user_policy_id), str(profile.get_create_date()), str(profile.get_modify_date()), str(profile.get_label()), str(profile.get_description()), str(profile.get_overridable()), str(profile.get_active()), str(profile.get_deleted()), str(profile.get_profile_data()), plugin_id]
                self.db_service.update('profile', profile_columns, profile_args)

        else:
            self.logger.debug('[ExecutionManager] Already there is user policy')

        policy = self.get_active_policies(policy.get_username())
        self.task_manager.addPolicy(policy)

    def get_active_policies(self, username):

        user_policy = self.db_service.select('policy', ['id', 'version', 'name'], ' type=\'U\' and name=\'' + username + '\'')
        ahenk_policy = self.db_service.select('policy', ['id', 'version'], ' type=\'A\' ')

        plugin_columns = ['id', 'active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date', 'name', 'policy_plugin', 'user_oriented', 'version']
        profile_columns = ['id', 'create_date', 'label', 'description', 'overridable', 'active', 'deleted', 'profile_data', 'modify_date', 'plugin']

        policy = PolicyBean(username=username)

        if len(user_policy) > 0:
            user_policy_version = user_policy[0][0]
            policy.set_user_policy_version(user_policy_version)
            user_profiles = self.db_service.select('profile', profile_columns, ' id=' + str(user_policy_version) + ' ')
            arr_profiles = []
            if len(user_profiles) > 0:
                for profile in user_profiles:
                    plu = self.db_service.select('plugin', plugin_columns, ' id=\'' + profile[9] + '\'')[0]
                    plugin = PluginBean(plu[0], plu[1], plu[2], plu[3], plu[4], plu[5], plu[6], plu[7], plu[8], plu[9], plu[10])

                    arr_profiles.append(ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6], profile[7], profile[8], plugin, policy.get_username()))
                policy.set_user_profiles(arr_profiles)

        if len(ahenk_policy) > 0:
            ahenk_policy_version = ahenk_policy[0][0]
            policy.set_ahenk_policy_version(ahenk_policy_version)
            ahenk_profiles = self.db_service.select('profile', profile_columns, ' id=' + str(ahenk_policy_version) + ' ')
            arr_profiles = []
            if len(ahenk_profiles) > 0:
                for profile in ahenk_profiles:
                    plu = self.db_service.select('plugin', plugin_columns, ' id=\'' + profile[9] + '\'')[0]
                    plugin = PluginBean(plu[0], plu[1], plu[2], plu[3], plu[4], plu[5], plu[6], plu[7], plu[8], plu[9], plu[10])

                    arr_profiles.append(ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6], profile[7], profile[8], plugin, policy.get_username()))
                policy.set_ahenk_profiles(arr_profiles)

        return policy

    def get_installed_plugins(self):
        plugins = self.db_service.select('plugin', ['name', 'version'])
        p_list = []
        for p in plugins:
            p_list.append(str(p[0]) + '-' + str(p[1]))
        return p_list

    def execute_task(self, arg):

        str_task = json.loads(arg)['task']
        json_task = json.loads(str_task)
        task = self.json_to_TaskBean(json_task)

        self.logger.debug('[ExecutionManager] Adding new  task...Task is:{}'.format(task.get_command_cls_id()))

        self.task_manager.addTask(task)
        self.logger.debug('[ExecutionManager] Task added')

    def json_to_TaskBean(self, json_data):

        plu = json_data['plugin']
        plugin = PluginBean(p_id=plu['id'], active=plu['active'], create_date=plu['createDate'], deleted=plu['deleted'], description=plu['description'], machine_oriented=plu['machineOriented'], modify_date=plu['modifyDate'], name=plu['name'], policy_plugin=plu['policyPlugin'], user_oriented=plu['userOriented'], version=plu['version'])

        return TaskBean(_id=json_data['id'], create_date=json_data['createDate'], modify_date=json_data['modifyDate'], command_cls_id=json_data['commandClsId'], parameter_map=json_data['parameterMap'], deleted=json_data['deleted'], plugin=plugin, cron_str=json_data['cronExpression'])

    def move_file(self, arg):
        default_file_path = self.config_manager.get('CONNECTION', 'receiveFileParam')
        j = json.loads(arg)
        # msg_id =str(j['id']).lower()
        target_file_path = str(j['filePath']).lower()
        file_name = str(j['filename']).lower()
        self.logger.debug('[ExecutionManager] ' + file_name + ' will be moved to ' + target_file_path)
        shutil.move(default_file_path + file_name, target_file_path + file_name)

    def execute_script(self, arg):
        j = json.loads(arg)
        # msg_id =str(j['id']).lower()
        file_path = str(j['filePath']).lower()
        time_stamp = str(j['timestamp']).lower()
        self.logger.debug('[ExecutionManager] Making executable file (%s) for execution' % file_path)
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)
        subprocess.call("/bin/sh " + file_path, shell=True)

    def retrive_file(self, arg):
        j = json.loads(arg)
        parameter_map = json.loads(json.dumps(j['parameterMap']))
        temp_file_path = self.config_manager.get('CONNECTION', 'receivefileparam')
        temp_file_name = str(uuid.uuid4())

        if str(j['protocol']).lower() == 'ssh':
            self.logger.debug('[ExecutionManager] Retrive file protocol is {}'.format(str(j['protocol']).lower()))
            host = parameter_map['host']
            username = parameter_map['username']
            password = parameter_map['password']
            port = parameter_map['port']
            path = parameter_map['path']

            transfer = FileTransfer(host, port, username, password)
            transfer.connect()
            transfer.get_file(temp_file_path + temp_file_name, path)
        elif str(j['protocol']).lower() == 'http':
            self.logger.debug('[ExecutionManager] Retrive file protocol is {}.'.format(str(j['protocol']).lower()))
            urllib.request.urlretrieve(parameter_map['url'], temp_file_path + temp_file_name)
        else:
            self.logger.debug('[ExecutionManager] Unsupported protocol is {}.'.format(str(j['protocol']).lower()))

        md5_hash = self.get_md5_file(temp_file_path + temp_file_name)
        os.rename(temp_file_path + temp_file_name, temp_file_path + md5_hash)

    def request_file(self, arg):
        j = json.loads(arg)
        # msg_id =str(j['id']).lower()
        file_path = str(j['filePath']).lower()
        time_stamp = str(j['timestamp']).lower()
        self.logger.debug('[ExecutionManager] Requested file is ' + file_path)
        self.messenger.send_file(file_path)

    def get_md5_file(self, fname):
        self.logger.debug('[ExecutionManager] md5 hashing')
        hash_md5 = hashlib.md5()
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return str(hash_md5.hexdigest())

    def json_to_PolicyBean(self, json_data):

        username = json_data['username']
        ahenk_prof_json_arr = json_data['agentPolicyProfiles']
        user_prof_json_arr = json_data['userPolicyProfiles']

        ahenk_prof_arr = []
        user_prof_arr = []
        if ahenk_prof_json_arr is not None:
            for prof in ahenk_prof_json_arr:
                plu = json.loads(json.dumps(prof['plugin']))
                plugin = PluginBean(p_id=plu['id'], active=plu['active'], create_date=plu['createDate'], deleted=plu['deleted'], description=plu['description'], machine_oriented=plu['machineOriented'], modify_date=plu['modifyDate'], name=plu['name'], policy_plugin=plu['policyPlugin'], user_oriented=plu['userOriented'], version=plu['version'])
                ahenk_prof_arr.append(ProfileBean(prof['id'], prof['createDate'], prof['label'], prof['description'], prof['overridable'], prof['active'], prof['deleted'], json.dumps(prof['profileData']), prof['modifyDate'], plugin, username))

        if user_prof_json_arr is not None:
            for prof in user_prof_json_arr:
                plu = json.loads(json.dumps(prof['plugin']))
                plugin = PluginBean(p_id=plu['id'], active=plu['active'], create_date=plu['createDate'], deleted=plu['deleted'], description=plu['description'], machine_oriented=plu['machineOriented'], modify_date=plu['modifyDate'], name=plu['name'], policy_plugin=plu['policyPlugin'], user_oriented=plu['userOriented'], version=plu['version'])
                user_prof_arr.append(ProfileBean(prof['id'], prof['createDate'], prof['label'], prof['description'], prof['overridable'], prof['active'], prof['deleted'], json.dumps(prof['profileData']), prof['modifyDate'], plugin, username))

        return PolicyBean(ahenk_policy_version=json_data['agentPolicyVersion'], user_policy_version=json_data['userPolicyVersion'], ahenk_profiles=ahenk_prof_arr, user_profiles=user_prof_arr, timestamp=json_data['timestamp'], username=json_data['username'], agent_execution_id=json_data['agentCommandExecutionId'], user_execution_id=json_data['userCommandExecutionId'])

    def install_deb(self, full_path):
        try:
            process = subprocess.Popen('gdebi -n ' + full_path, shell=True)
            process.wait()
        except Exception as e:
            self.logger.error('[ExecutionManager] Deb package couldn\'t install properly. Error Message: {}'.format(str(e)))

    def remove_file(self, full_path):
        try:
            subprocess.Popen('rm ' + full_path, shell=True)
            self.logger.debug('[ExecutionManager] Removed file is {}'.format(full_path))
        except Exception as e:
            self.logger.debug('[ExecutionManager] File couldn\'t removed. Error Message: {}'.format(str(e)))
