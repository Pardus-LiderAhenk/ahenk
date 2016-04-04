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
from base.model.Policy import Policy
from base.model.PolicyBean import PolicyBean
from base.model.ProfileBean import ProfileBean
from base.model.Task import Task
from base.model.MessageType import MessageType


class ExecutionManager(object):
    """docstring for FileTransferManager"""

    def __init__(self):
        super(ExecutionManager, self).__init__()

        scope = Scope.getInstance()
        self.config_manager = scope.getConfigurationManager()
        self.event_manager = scope.getEventManager()
        self.task_manager = scope.getTaskManager()
        self.messager = scope.getMessager()
        self.logger = scope.getLogger()
        self.db_service = scope.getDbService()

        # TODO DEBUG
        self.event_manager.register_event(str(MessageType.EXECUTE_SCRIPT), self.execute_script)
        self.event_manager.register_event(str(MessageType.REQUEST_FILE), self.request_file)
        self.event_manager.register_event(str(MessageType.MOVE_FILE), self.move_file)
        self.event_manager.register_event(str(MessageType.EXECUTE_TASK), self.execute_task)
        self.event_manager.register_event('EXECUTE_POLICY', self.execute_policy)

    def execute_policy(self, arg):
        self.logger.debug('[ExecutionManager] Updating policies...')

        policy = Policy(json.loads(arg))
        # TODO get username and machine uid
        username = policy.username
        machine_uid = self.db_service.select_one_result('registration', 'jid', 'registered=1')

        ahenk_policy_ver = self.db_service.select_one_result('policy', 'version', 'type = \'A\'')
        user_policy_version = self.db_service.select_one_result('policy', 'version', 'type = \'U\' and name = \'' + username + '\'')
        installed_plugins = self.get_installed_plugins()
        missing_plugins = []
        profile_columns = ['id', 'create_date', 'modify_date', 'label', 'description', 'overridable', 'active', 'deleted', 'profile_data', 'plugin']

        if policy.ahenk_policy_version != ahenk_policy_ver:
            ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')
            if ahenk_policy_id is not None:
                self.db_service.delete('profile', 'id=' + str(ahenk_policy_id))
                self.db_service.update('policy', ['version'], [str(policy.ahenk_policy_version)], 'type=\'A\'')
            else:
                self.db_service.update('policy', ['type', 'version', 'name'], ['A', str(policy.ahenk_policy_version), machine_uid])
                ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')

            for profile in policy.ahenk_profiles:
                args = [str(ahenk_policy_id), str(profile.create_date), str(profile.modify_date), str(profile.label),
                        str(profile.description), str(profile.overridable), str(profile.active), str(profile.deleted), str(profile.profile_data), str(profile.plugin)]
                self.db_service.update('profile', profile_columns, args)
                if profile.plugin.name not in installed_plugins and profile.plugin.name not in missing_plugins:
                    missing_plugins.append(profile.plugin.name)

        else:
            self.logger.debug('[ExecutionManager] Already there is ahenk policy')

        if policy.user_policy_version != user_policy_version:
            user_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'U\' and name=\'' + username + '\'')
            if user_policy_id is not None:
                self.db_service.delete('profile', 'id=' + str(user_policy_id))
                self.db_service.update('policy', ['version'], [str(policy.user_policy_version)], 'type=\'U\' and name=\'' + username + '\'')
            else:
                self.db_service.update('policy', ['type', 'version', 'name'], ['U', str(policy.user_policy_version), username])
                user_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'U\' and name=\'' + username + '\'')

            for profile in policy.user_profiles:
                args = [int(user_policy_id), str(profile.create_date), str(profile.modify_date), str(profile.label),
                        str(profile.description), int(profile.overridable), int(profile.active), int(profile.deleted), str(profile.profile_data), str(profile.plugin.to_string())]
                self.db_service.update('profile', profile_columns, args)
                if profile.plugin.name not in installed_plugins and profile.plugin.name not in missing_plugins:
                    missing_plugins.append(profile.plugin.name)
        else:
            self.logger.debug('[ExecutionManager] Already there is user policy')

        # TODO check plugins
        print("but first need these plugins:" + str(missing_plugins))

        self.task_manager.addPolicy(self.get_active_policies(username))

    def get_active_policies(self, username):

        """
            self.ahenk_policy_version = ahenk_policy_version
            self.user_policy_version = user_policy_version
            self.ahenk_profiles = ahenk_profiles
            self.user_profiles = user_profiles
        self.timestamp = timestamp
            self.username = username


        self.ahenk_execution_id = ahenk_execution_id
        self.user_execution_id = user_execution_id
        """

        user_policy = self.db_service.select('policy', ['id', 'version', 'name'], ' type=\'U\' and name=\'' + username + '\'')
        ahenk_policy = self.db_service.select('policy', ['id', 'version'], ' type=\'A\' ')

        policy = PolicyBean(username=username)

        if len(user_policy) > 0:
            user_policy_version = user_policy[0][0]
            policy.set_user_policy_version(user_policy_version)
            user_profiles = self.db_service.select('profile', ['id', 'create_date', 'label', 'description', 'overridable', 'active', 'deleted', 'profile_data', 'modify_date', 'plugin'], ' id=' + str(user_policy_version) + ' ')

            arr_profiles = []
            if len(user_profiles) > 0:
                for profile in user_profiles:
                    arr_profiles.append(ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6], profile[7], profile[8], profile[9]))
                policy.set_user_profiles(arr_profiles)

        if len(ahenk_policy) > 0:
            ahenk_policy_version = ahenk_policy[0][0]
            policy.set_ahenk_policy_version(ahenk_policy_version)
            ahenk_profiles = self.db_service.select('profile', ['id', 'create_date', 'label', 'description', 'overridable', 'active', 'deleted', 'profile_data', 'modify_date', 'plugin'], ' id=' + str(ahenk_policy_version) + ' ')
            arr_profiles = []
            if len(ahenk_profiles) > 0:
                for profile in user_profiles:
                    arr_profiles.append(ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5], profile[6], profile[7], profile[8], profile[9]))
                policy.set_ahenk_profiles(arr_profiles)

        print("")
        return policy


    def get_installed_plugins(self):
        plugins = self.db_service.select('plugin', ['name', 'version'])
        p_list = []
        for p in plugins:
            p_list.append(str(p[0]) + '-' + str(p[1]))
        return p_list

    def execute_task(self, arg):
        self.logger.debug('[ExecutionManager] Adding new  task...')
        task = Task(json.loads(arg))
        self.task_manager.addTask(task)
        self.logger.debug('[ExecutionManager] Task added')

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

    # need to move somewhere else
    def request_file(self, arg):
        j = json.loads(arg)
        # msg_id =str(j['id']).lower()
        file_path = str(j['filePath']).lower()
        time_stamp = str(j['timestamp']).lower()
        self.logger.debug('[ExecutionManager] Requested file is ' + file_path)
        self.messager.send_file(file_path)

    def get_md5_file(self, fname):
        self.logger.debug('[ExecutionManager] md5 hashing')
        hash_md5 = hashlib.md5()
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return str(hash_md5.hexdigest())
