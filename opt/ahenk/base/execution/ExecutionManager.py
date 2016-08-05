#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import hashlib
import json
import os
import shutil
import stat
import subprocess

from base.Scope import Scope
from base.util.util import Util
from base.model.PluginBean import PluginBean
from base.model.PolicyBean import PolicyBean
from base.model.ProfileBean import ProfileBean
from base.model.TaskBean import TaskBean
from base.model.enum.MessageType import MessageType
from base.file.file_transfer_manager import FileTransferManager
from base.system.system import System


class ExecutionManager(object):
    """docstring for FileTransferManager"""

    # TODO more logs
    def __init__(self):
        super(ExecutionManager, self).__init__()

        scope = Scope.getInstance()
        self.config_manager = scope.getConfigurationManager()
        self.event_manager = scope.getEventManager()
        self.task_manager = scope.getTaskManager()
        self.messenger = scope.getMessenger()
        self.logger = scope.getLogger()
        self.db_service = scope.getDbService()
        self.message_manager = scope.getMessageManager()
        self.plugin_manager = scope.getPluginManager()
        self.policy_executed = {}

        self.event_manager.register_event(MessageType.EXECUTE_SCRIPT.value, self.execute_script)
        # send file ahenk to lider
        self.event_manager.register_event(MessageType.REQUEST_FILE.value, self.request_file)
        # send file lider to ahenk
        self.event_manager.register_event(MessageType.RETRIVE_FILE.value, self.retrieve_file)
        self.event_manager.register_event(MessageType.MOVE_FILE.value, self.move_file)
        self.event_manager.register_event(MessageType.EXECUTE_TASK.value, self.execute_task)
        self.event_manager.register_event(MessageType.EXECUTE_POLICY.value, self.execute_policy)
        self.event_manager.register_event(MessageType.INSTALL_PLUGIN.value, self.install_plugin)
        self.event_manager.register_event(MessageType.RESPONSE_AGREEMENT.value, self.agreement_update)

    def agreement_update(self, arg):

        try:
            json_data = json.loads(arg)
            transfer_manager = FileTransferManager(json_data['protocol'], json_data['parameterMap'])

            transfer_manager.transporter.connect()
            file_name = transfer_manager.transporter.get_file()
            transfer_manager.transporter.disconnect()

            agreement_content = Util.read_file(System.Ahenk.received_dir_path() + file_name)
            Util.delete_file(System.Ahenk.received_dir_path() + file_name)
            # TODO
            title = 'Kullanıcı Sözleşmesi'

            if agreement_content is not None and agreement_content != '':
                old_content = self.db_service.select_one_result('contract', 'content',
                                                                'id =(select MAX(id) from contract)')
                if old_content is None or Util.get_md5_text(old_content) != Util.get_md5_text(agreement_content):
                    self.db_service.update('contract', self.db_service.get_cols('contract'),
                                           [agreement_content, title, json_data['timestamp']])
        except Exception as e:
            self.logger.error(
                '[ExecutionManager] A problem occurred while updating agreement. Error Message : {}'.format(str(e)))

    def install_plugin(self, arg):
        plugin = json.loads(arg)
        self.logger.debug('[ExecutionManager] Installing missing plugin')
        try:
            plugin_name = plugin['pluginName']
            plugin_version = plugin['pluginVersion']

            try:
                transfer_manager = FileTransferManager(plugin['protocol'], plugin['parameterMap'])
                transfer_manager.transporter.connect()
                file_name = transfer_manager.transporter.get_file()
                transfer_manager.transporter.disconnect()
                downloaded_file = System.Ahenk.received_dir_path() + file_name
            except Exception as e:
                self.logger.error(
                    '[ExecutionManager] Plugin package could not fetch. Error Message: {}.'.format(str(e)))
                self.logger.error('[ExecutionManager] Plugin Installation is cancelling')
                return

            try:
                Util.install_with_gdebi(downloaded_file)
                self.logger.debug('[ExecutionManager] Plugin installed.')
            except Exception as e:
                self.logger.error('[ExecutionManager] Could not install plugin. Error Message: {}'.format(str(e)))
                return

            try:
                self.remove_file(downloaded_file)
                self.logger.debug('[ExecutionManager] Temp files were removed.')
            except Exception as e:
                self.logger.error('[ExecutionManager] Could not remove temp file. Error Message: {}'.format(str(e)))

            self.plugin_manager.load_single_plugin(plugin_name)

        except Exception as e:
            self.logger.error(
                '[ExecutionManager] A problem occurred while installing new Ahenk plugin. Error Message:{}'.format(
                    str(e)))

    def is_policy_executed(self, username):
        if username in self.policy_executed:
            return self.policy_executed[username]
        return False

    def remove_user_executed_policy_dict(self, username):
        if username in self.policy_executed:
            self.policy_executed[username] = False

    def execute_default_policy(self, username):
        self.logger.debug('[ExecutionManager] Executing active policies for {} user...'.format(username))
        self.task_manager.addPolicy(self.get_active_policies(username))

    def execute_policy(self, arg):
        self.logger.debug('[ExecutionManager] Updating policies...')
        policy = self.json_to_PolicyBean(json.loads(arg))
        self.policy_executed[policy.get_username()] = True
        machine_uid = self.db_service.select_one_result('registration', 'jid', 'registered=1')
        ahenk_policy_ver = self.db_service.select_one_result('policy', 'version', 'type = \'A\'')
        user_policy_version = self.db_service.select_one_result('policy', 'version',
                                                                'type = \'U\' and name = \'' + policy.get_username() + '\'')

        profile_columns = ['id', 'create_date', 'modify_date', 'label', 'description', 'overridable', 'active',
                           'deleted', 'profile_data', 'plugin']
        plugin_columns = ['active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date', 'name',
                          'policy_plugin', 'user_oriented', 'version', 'task_plugin', 'x_based']

        if policy.get_ahenk_policy_version() != ahenk_policy_ver:
            ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')
            if ahenk_policy_id is not None:
                self.db_service.delete('profile', 'id=' + str(ahenk_policy_id))
                self.db_service.delete('plugin', 'id=' + str(ahenk_policy_id))
                self.db_service.update('policy', ['version'], [str(policy.get_ahenk_policy_version())], 'type=\'A\'')
            else:
                self.db_service.update('policy', ['type', 'version', 'name', 'execution_id'],
                                       ['A', str(policy.get_ahenk_policy_version()), machine_uid,
                                        policy.get_agent_execution_id()])
                ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')

            for profile in policy.get_ahenk_profiles():
                plugin = profile.get_plugin()

                plugin_args = [str(plugin.get_active()), str(plugin.get_create_date()), str(plugin.get_deleted()),
                               str(plugin.get_description()), str(plugin.get_machine_oriented()),
                               str(plugin.get_modify_date()), str(plugin.get_name()), str(plugin.get_policy_plugin()),
                               str(plugin.get_user_oriented()), str(plugin.get_version()),
                               str(plugin.get_task_plugin()), str(plugin.get_x_based())]
                plugin_id = self.db_service.update('plugin', plugin_columns, plugin_args)

                profile_args = [str(ahenk_policy_id), str(profile.get_create_date()), str(profile.get_modify_date()),
                                str(profile.get_label()), str(profile.get_description()),
                                str(profile.get_overridable()), str(profile.get_active()), str(profile.get_deleted()),
                                str(profile.get_profile_data()), plugin_id]
                self.db_service.update('profile', profile_columns, profile_args)

        else:
            self.logger.debug('[ExecutionManager] Already there is ahenk policy. Command Execution Id is updating')
            self.db_service.update('policy', ['execution_id'], [policy.get_agent_execution_id()], 'type = \'A\'')

        if policy.get_user_policy_version() != user_policy_version:
            user_policy_id = self.db_service.select_one_result('policy', 'id',
                                                               'type = \'U\' and name=\'' + policy.get_username() + '\'')
            if user_policy_id is not None:
                # TODO remove profiles' plugins
                self.db_service.delete('profile', 'id=' + str(user_policy_id))
                self.db_service.delete('plugin', 'id=' + str(user_policy_id))
                self.db_service.update('policy', ['version'], [str(policy.get_user_policy_version())],
                                       'type=\'U\' and name=\'' + policy.get_username() + '\'')
            else:
                self.db_service.update('policy', ['type', 'version', 'name', 'execution_id'],
                                       ['U', str(policy.get_user_policy_version()), policy.get_username(),
                                        policy.get_user_execution_id()])
                user_policy_id = self.db_service.select_one_result('policy', 'id',
                                                                   'type = \'U\' and name=\'' + policy.get_username() + '\'')

            for profile in policy.get_user_profiles():
                plugin = profile.get_plugin()

                plugin_args = [str(plugin.get_active()), str(plugin.get_create_date()), str(plugin.get_deleted()),
                               str(plugin.get_description()), str(plugin.get_machine_oriented()),
                               str(plugin.get_modify_date()), str(plugin.get_name()), str(plugin.get_policy_plugin()),
                               str(plugin.get_user_oriented()), str(plugin.get_version()),
                               str(plugin.get_task_plugin()), str(plugin.get_x_based())]
                plugin_id = self.db_service.update('plugin', plugin_columns, plugin_args)

                profile_args = [str(user_policy_id), str(profile.get_create_date()), str(profile.get_modify_date()),
                                str(profile.get_label()), str(profile.get_description()),
                                str(profile.get_overridable()), str(profile.get_active()), str(profile.get_deleted()),
                                str(profile.get_profile_data()), plugin_id]
                self.db_service.update('profile', profile_columns, profile_args)

        else:
            self.logger.debug('[ExecutionManager] Already there is user policy. . Command Execution Id is updating')
            self.db_service.update('policy', ['execution_id'], [policy.get_user_execution_id()], 'type = \'U\'')

        policy = self.get_active_policies(policy.get_username())
        self.task_manager.addPolicy(policy)

    def get_active_policies(self, username):

        user_policy = self.db_service.select('policy', ['id', 'version', 'name'],
                                             ' type=\'U\' and name=\'' + username + '\'')
        ahenk_policy = self.db_service.select('policy', ['id', 'version'], ' type=\'A\' ')

        plugin_columns = ['id', 'active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date',
                          'name', 'policy_plugin', 'user_oriented', 'version', 'task_plugin', 'x_based']
        profile_columns = ['id', 'create_date', 'label', 'description', 'overridable', 'active', 'deleted',
                           'profile_data', 'modify_date', 'plugin']

        policy = PolicyBean(username=username)

        if len(user_policy) > 0:
            user_policy_version = user_policy[0][0]
            policy.set_user_policy_version(user_policy_version)
            user_profiles = self.db_service.select('profile', profile_columns, ' id=' + str(user_policy_version) + ' ')
            arr_profiles = []
            if len(user_profiles) > 0:
                for profile in user_profiles:
                    plu = self.db_service.select('plugin', plugin_columns, ' id=\'' + profile[9] + '\'')[0]
                    plugin = PluginBean(p_id=plu[0], active=plu[1], create_date=plu[2], deleted=plu[3],
                                        description=plu[4], machine_oriented=plu[5], modify_date=plu[6], name=plu[7],
                                        policy_plugin=plu[8], user_oriented=plu[9], version=plu[10],
                                        task_plugin=plu[11], x_based=plu[12])

                    arr_profiles.append(
                        ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6],
                                    profile[7], profile[8], plugin, policy.get_username()))
                policy.set_user_profiles(arr_profiles)

        if len(ahenk_policy) > 0:
            ahenk_policy_version = ahenk_policy[0][0]
            policy.set_ahenk_policy_version(ahenk_policy_version)
            ahenk_profiles = self.db_service.select('profile', profile_columns,
                                                    ' id=' + str(ahenk_policy_version) + ' ')
            arr_profiles = []
            if len(ahenk_profiles) > 0:
                for profile in ahenk_profiles:
                    plu = self.db_service.select('plugin', plugin_columns, ' id=\'' + profile[9] + '\'')[0]
                    plugin = PluginBean(p_id=plu[0], active=plu[1], create_date=plu[2], deleted=plu[3],
                                        description=plu[4], machine_oriented=plu[5], modify_date=plu[6], name=plu[7],
                                        policy_plugin=plu[8], user_oriented=plu[9], version=plu[10],
                                        task_plugin=plu[11], x_based=plu[12])

                    arr_profiles.append(
                        ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6],
                                    profile[7], profile[8], plugin, policy.get_username()))
                policy.set_ahenk_profiles(arr_profiles)

        return policy

    # from db
    def get_installed_plugins(self):
        plugins = self.db_service.select('plugin', ['name', 'version'])
        p_list = []
        for p in plugins:
            p_list.append(str(p[0]) + '-' + str(p[1]))
        return p_list

    def execute_task(self, arg):

        json_task = json.loads(arg)['task']
        json_task = json.loads(json_task)
        json_server_conf = json.dumps(json.loads(arg)['fileServerConf'])

        task = self.json_to_task_bean(json_task, json_server_conf)
        self.logger.debug('[ExecutionManager] Adding new  task...Task is:{}'.format(task.get_command_cls_id()))

        self.task_manager.addTask(task)
        self.logger.debug('[ExecutionManager] Task added')

    def json_to_task_bean(self, json_data, file_server_conf=None):
        plu = json_data['plugin']
        plugin = PluginBean(p_id=plu['id'], active=plu['active'], create_date=plu['createDate'], deleted=plu['deleted'],
                            description=plu['description'], machine_oriented=plu['machineOriented'],
                            modify_date=plu['modifyDate'], name=plu['name'], policy_plugin=plu['policyPlugin'],
                            user_oriented=plu['userOriented'], version=plu['version'], task_plugin=plu['taskPlugin'],
                            x_based=plu['xBased'])
        return TaskBean(_id=json_data['id'], create_date=json_data['createDate'], modify_date=json_data['modifyDate'],
                        command_cls_id=json_data['commandClsId'], parameter_map=json_data['parameterMap'],
                        deleted=json_data['deleted'], plugin=plugin, cron_str=json_data['cronExpression'],
                        file_server=str(file_server_conf))

    def move_file(self, arg):
        default_file_path = System.Ahenk.received_dir_path()
        j = json.loads(arg)
        # msg_id =str(j['id']).lower()
        target_file_path = str(j['filePath']).lower()
        file_name = str(j['filename']).lower()
        self.logger.debug('[ExecutionManager] ' + file_name + ' will be moved to ' + target_file_path)
        shutil.move(default_file_path + file_name, target_file_path + file_name)

    def execute_script(self, arg):
        try:
            self.logger.debug('[ExecutionManager] Executing script...')
            messenger = Scope().getInstance().getMessenger()

            json_data = json.loads(arg)
            result_code, p_out, p_err = Util.execute(str(json_data['command']))

            self.logger.debug('[ExecutionManager] Executed script')

            data = {}
            data['type'] = 'SCRIPT_RESULT'
            data['timestamp'] = str(Util.timestamp())

            if result_code == 0:
                self.logger.debug('[ExecutionManager] Command execution was finished successfully')
                try:
                    temp_name = str(Util.generate_uuid())
                    temp_full_path = System.Ahenk.received_dir_path() + temp_name
                    self.logger.debug('[ExecutionManager] Writing result to file')
                    Util.write_file(temp_full_path, str(p_out))
                    md5 = Util.get_md5_file(temp_full_path)
                    Util.rename_file(temp_full_path, System.Ahenk.received_dir_path() + md5)

                    file_manager = FileTransferManager(json_data['fileServerConf']['protocol'],
                                                       json_data['fileServerConf']['parameterMap'])
                    file_manager.transporter.connect()
                    self.logger.debug('[ExecutionManager] File transfer connection was created')
                    success = file_manager.transporter.send_file(System.Ahenk.received_dir_path() + md5, md5)
                    self.logger.debug('[ExecutionManager] File was transferred')
                    file_manager.transporter.disconnect()
                    self.logger.debug('[ExecutionManager] File transfer connection was closed')

                    if success is False:
                        self.logger.error('[ExecutionManager] A problem occurred while file transferring')
                        data['resultCode'] = '-1'
                        data[
                            'errorMessage'] = 'Command executed successfully but a problem occurred while sending result file'

                    else:
                        data['md5'] = md5

                except Exception as e:
                    self.logger.error(
                        '[ExecutionManager] A problem occurred while file transferring. Error Message :{0}'.format(
                            str(e)))
                    raise
            else:
                self.logger.error(
                    '[ExecutionManager] Command execution was failed. Error Message :{0}'.format(str(result_code)))
                data['resultCode'] = str(result_code)
                data['errorMessage'] = str(p_err)

            messenger.send_direct_message(json.dumps(data))
        except Exception as e:
            self.logger.error(
                '[ExecutionManager] A problem occurred while running execute script action. Error Message :{}'.format(
                    str(e)))

    def retrieve_file(self, arg):
        self.logger.debug('[ExecutionManager] Retrieving file ...')
        try:
            json_data = json.loads(arg)
            self.logger.debug('[ExecutionManager] Retrieving file protocol is {}'.format(str(json_data['protocol'])))
            transfer_manager = FileTransferManager(json_data['protocol'], json_data['parameterMap'])
            transfer_manager.transporter.connect()
            file_name = transfer_manager.transporter.get_file()
            transfer_manager.transporter.disconnect()
            downloaded_file = Util.read_file(System.Ahenk.received_dir_path() + file_name)
            self.logger.debug(
                '[ExecutionManager] Retrieving file is completed successfully. Full path of file is {}'.format(
                    downloaded_file))
        except Exception as e:
            self.logger.debug(
                '[ExecutionManager] A problem occurred while retrieving file. Error Message: {}'.format(str(e)))

    def request_file(self, arg):
        # TODO  change to new transfer way
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
                plugin = PluginBean(p_id=plu['id'], active=plu['active'], create_date=plu['createDate'],
                                    deleted=plu['deleted'], description=plu['description'],
                                    machine_oriented=plu['machineOriented'], modify_date=plu['modifyDate'],
                                    name=plu['name'], policy_plugin=plu['policyPlugin'],
                                    user_oriented=plu['userOriented'], version=plu['version'],
                                    task_plugin=plu['taskPlugin'], x_based=plu['xBased'])
                ahenk_prof_arr.append(
                    ProfileBean(prof['id'], prof['createDate'], prof['label'], prof['description'], prof['overridable'],
                                prof['active'], prof['deleted'], json.dumps(prof['profileData']), prof['modifyDate'],
                                plugin, username))

        if user_prof_json_arr is not None:
            for prof in user_prof_json_arr:
                plu = json.loads(json.dumps(prof['plugin']))
                plugin = PluginBean(p_id=plu['id'], active=plu['active'], create_date=plu['createDate'],
                                    deleted=plu['deleted'], description=plu['description'],
                                    machine_oriented=plu['machineOriented'], modify_date=plu['modifyDate'],
                                    name=plu['name'], policy_plugin=plu['policyPlugin'],
                                    user_oriented=plu['userOriented'], version=plu['version'],
                                    task_plugin=plu['taskPlugin'], x_based=plu['xBased'])
                user_prof_arr.append(
                    ProfileBean(prof['id'], prof['createDate'], prof['label'], prof['description'], prof['overridable'],
                                prof['active'], prof['deleted'], json.dumps(prof['profileData']), prof['modifyDate'],
                                plugin, username))

        return PolicyBean(ahenk_policy_version=json_data['agentPolicyVersion'],
                          user_policy_version=json_data['userPolicyVersion'], ahenk_profiles=ahenk_prof_arr,
                          user_profiles=user_prof_arr, timestamp=json_data['timestamp'], username=json_data['username'],
                          agent_execution_id=json_data['agentCommandExecutionId'],
                          user_execution_id=json_data['userCommandExecutionId'])

    def remove_file(self, full_path):
        try:
            subprocess.Popen('rm ' + full_path, shell=True)
            self.logger.debug('[ExecutionManager] Removed file is {}'.format(full_path))
        except Exception as e:
            self.logger.debug('[ExecutionManager] File couldn\'t removed. Error Message: {}'.format(str(e)))
