#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import time
from base.file.file_transfer_manager import FileTransferManager
from base.model.enum.content_type import ContentType
from base.model.enum.message_code import MessageCode
from base.model.enum.message_type import MessageType
from base.model.plugin_bean import PluginBean
from base.model.policy_bean import PolicyBean
from base.model.profile_bean import ProfileBean
from base.model.response import Response
from base.model.task_bean import TaskBean
from base.scheduler.custom.schedule_job import ScheduleTaskJob
from base.scope import Scope
from base.system.system import System
from base.util.util import Util
from easygui import *


class ExecutionManager(object):
    """docstring for FileTransferManager"""

    # TODO more logs
    def __init__(self):
        super(ExecutionManager, self).__init__()

        scope = Scope.get_instance()
        self.config_manager = scope.get_configuration_manager()
        self.event_manager = scope.get_event_manager()
        self.task_manager = scope.get_task_manager()
        self.messenger = scope.get_messenger()
        self.logger = scope.get_logger()
        self.db_service = scope.get_db_service()
        self.message_manager = scope.get_message_manager()
        self.plugin_manager = scope.get_plugin_manager()
        self.policy_executed = dict()

        self.event_manager.register_event(MessageType.EXECUTE_SCRIPT.value, self.execute_script)
        self.event_manager.register_event(MessageType.EXECUTE_TASK.value, self.execute_task)
        self.event_manager.register_event(MessageType.EXECUTE_POLICY.value, self.execute_policy)
        self.event_manager.register_event(MessageType.INSTALL_PLUGIN.value, self.install_plugin)
        self.event_manager.register_event(MessageType.RESPONSE_AGREEMENT.value, self.agreement_update)
        self.event_manager.register_event(MessageType.UPDATE_SCHEDULED_TASK.value, self.update_scheduled_task)
        self.event_manager.register_event(MessageType.REGISTRATION_RESPONSE.value, self.unregister) # registration message for unregister event

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
            self.logger.warning(
                'A problem occurred while updating agreement. Error Message : {0}'.format(str(e)))

    def install_plugin(self, arg):
        plugin = json.loads(arg)
        self.logger.debug('Installing missing plugin')
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
                    'Plugin package could not fetch. Error Message: {0}.'.format(str(e)))
                self.logger.error('Plugin Installation is cancelling')
                self.plugin_installation_failure(plugin_name, plugin_version)
                return

            try:
                Util.install_with_dpkg(downloaded_file)
                self.logger.debug('Plugin installed.')
            except Exception as e:
                self.logger.error('Could not install plugin. Error Message: {0}'.format(str(e)))
                self.plugin_installation_failure(plugin_name, plugin_version)
                return

            try:
                Util.delete_file(downloaded_file)
                self.logger.debug('Temp files were removed.')
            except Exception as e:
                self.logger.error('Could not remove temp file. Error Message: {0}'.format(str(e)))

        except Exception as e:
            self.logger.error(
                'A problem occurred while installing new Ahenk plugin. Error Message:{0}'.format(
                    str(e)))

    def plugin_installation_failure(self, plugin_name, plugin_version):

        self.logger.warning('{0} plugin installation failure '.format(plugin_name))

        if plugin_name in self.plugin_manager.delayed_profiles.keys():
            profile = self.plugin_manager.delayed_profiles[plugin_name]
            self.logger.warning('An error message sending with related profile properties...')
            related_policy = self.db_service.select('policy', ['version', 'execution_id'],
                                                    'id={0}'.format(profile.get_id()))
            data = dict()
            data['message'] = "Profil işletilirken eklenti bulunamadı "
            "ve eksik olan eklenti kurulmaya çalışırken hata ile karşılaşıldı. "
            "İlgili eklenti Ahenk'e yüklendiğinde, başarısız olan bu profil "
            "(Başka bir politika tarafından ezilmedikçe) "
            "çalıştırılacaktır"
            " Sorunu çözmek için Lider yapılandırma dosyasındaki eklenti dağıtım "
            "bilgilerinin doğruluğundan ve belirtilen dizinde geçerli eklenti paketinin "
            "bulunduğundan emin olun."
            response = Response(type=MessageType.POLICY_STATUS.value, id=profile.get_id(),
                                code=MessageCode.POLICY_ERROR.value,
                                message="Profil işletilirken eklenti bulunamadı "
                                        "ve eksik olan eklenti kurulurken hata oluştu",
                                execution_id=related_policy[0][1], policy_version=related_policy[0][0],
                                data=json.dumps(data), content_type=ContentType.APPLICATION_JSON.value)
            messenger = Scope.get_instance().get_messenger()
            messenger.send_direct_message(self.message_manager.policy_status_msg(response))
            self.logger.warning(
                'Error message was sent about {0} plugin installation failure while trying to run a profile')

        if plugin_name in self.plugin_manager.delayed_tasks.keys():
            task = self.plugin_manager.delayed_tasks[plugin_name]
            self.logger.warning('An error message sending with related task properties...')

            data = dict()
            data['message'] = "Görev işletilirken eklenti bulunamadı "
            "ve eksik olan eklenti kurulmaya çalışırken hata ile karşılaşıldı. "
            "İlgili eklenti Ahenk'e yüklendiğinde, başarısız olan bu görev "
            "çalıştırılacaktır"
            " Sorunu çözmek için Lider yapılandırma dosyasındaki eklenti dağıtım "
            "bilgilerinin doğruluğundan ve belirtilen dizinde geçerli eklenti paketinin "
            "bulunduğundan emin olun."
            response = Response(type=MessageType.TASK_STATUS.value, id=task.get_id(),
                                code=MessageCode.TASK_ERROR.value,
                                message="Görev işletilirken eklenti bulunamadı "
                                        "ve eksik olan eklenti kurulmaya çalışırken oluştu.",
                                data=json.dumps(data), content_type=ContentType.APPLICATION_JSON.value)
            messenger = Scope.get_instance().get_messenger()
            messenger.send_direct_message(self.message_manager.task_status_msg(response))
            self.logger.warning(
                'Error message was sent about {0} plugin installation failure while trying to run a task')

    def is_policy_executed(self, username):
        if username in self.policy_executed:
            return self.policy_executed[username]
        return False

    def remove_user_executed_policy_dict(self, username):
        if username in self.policy_executed:
            self.policy_executed[username] = False

    def execute_default_policy(self, username):
        self.logger.debug('Executing active policies for {0} user...'.format(username))
        self.task_manager.addPolicy(self.get_active_policies(username))

    def update_scheduled_task(self, arg):
        self.logger.debug('Working on scheduled task ...')
        update_scheduled_json = json.loads(arg)
        scheduler = Scope.get_instance().get_scheduler()

        if str(update_scheduled_json['cronExpression']).lower() == 'none' or update_scheduled_json[
            'cronExpression'] is None:
            self.logger.debug('Scheduled task will be removed')
            scheduler.remove_job(int(update_scheduled_json['taskId']))
            self.logger.debug('Task removed from scheduled database')
            self.db_service.update('task', ['deleted'], ['True'],
                                   'id={0}'.format(update_scheduled_json['taskId']))
            self.logger.debug('Task table updated.')
        else:
            self.logger.debug('Scheduled task cron expression will be updated.')
            self.db_service.update('task', ['cron_expr'], [str(update_scheduled_json['cronExpression'])],
                                   'id={0}'.format(update_scheduled_json['taskId']))
            self.logger.debug('Task table updated.')
            scheduler.remove_job(str(update_scheduled_json['taskId']))
            self.logger.debug('Previous scheduled task removed.')
            scheduler.add_job(ScheduleTaskJob(self.get_task_bean_by_id(update_scheduled_json['taskId'])))
            self.logger.debug('New scheduled task added')

    def get_task_bean_by_id(self, task_id):

        task_row = self.db_service.select('task', self.db_service.get_cols('task'), 'id={0}'.format(task_id))[0]
        task = TaskBean(task_row[0], task_row[1], task_row[2], task_row[3], task_row[4], task_row[5],
                        self.get_plugin_bean_by_id(task_row[6]),
                        task_row[7], task_row[8])
        return task

    def get_plugin_bean_by_id(self, plugin_id):
        plugin_row = self.db_service.select('plugin', self.db_service.get_cols('plugin'), 'id={0}'.format(plugin_id))[0]
        plugin = PluginBean(plugin_row[0], plugin_row[1], plugin_row[2], plugin_row[3], plugin_row[4], plugin_row[5],
                            plugin_row[6], plugin_row[7], plugin_row[8], plugin_row[11], plugin_row[9], plugin_row[10],
                            plugin_row[12])
        return plugin

    def execute_policy(self, arg):
        try:
            self.logger.debug('Updating policies...')
            policy = self.json_to_PolicyBean(json.loads(arg))
            self.policy_executed[policy.get_username()] = True
            machine_uid = self.db_service.select_one_result('registration', 'jid', 'registered=1')
            ahenk_policy_ver = self.db_service.select_one_result('policy', 'version', 'type = \'A\'')
            user_policy_version = self.db_service.select_one_result('policy', 'version',
                                                                    'type = \'U\' and name = \'' + policy.get_username() + '\'')

            profile_columns = ['id', 'create_date', 'modify_date', 'label', 'description', 'overridable', 'active',
                               'deleted', 'profile_data', 'plugin']
            plugin_columns = ['active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date',
                              'name',
                              'policy_plugin', 'user_oriented', 'version', 'task_plugin', 'x_based']

            if policy.get_ahenk_policy_version() != ahenk_policy_ver:
                ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')
                if ahenk_policy_id is not None:
                    self.db_service.delete('profile', 'id=' + str(ahenk_policy_id))
                    self.db_service.delete('plugin', 'id=' + str(ahenk_policy_id))
                    self.db_service.update('policy', ['version', 'execution_id', 'expiration_date'],
                                           [str(policy.get_ahenk_policy_version()), policy.agent_execution_id,
                                            str(policy.agent_expiration_date)], 'type=\'A\'')
                else:
                    self.db_service.update('policy', ['type', 'version', 'name', 'execution_id', 'expiration_date'],
                                           ['A', str(policy.get_ahenk_policy_version()), machine_uid,
                                            policy.get_agent_execution_id(), policy.agent_expiration_date])
                    ahenk_policy_id = self.db_service.select_one_result('policy', 'id', 'type = \'A\'')

                for profile in policy.get_ahenk_profiles():
                    plugin = profile.get_plugin()

                    plugin_args = [str(plugin.get_active()), str(plugin.get_create_date()), str(plugin.get_deleted()),
                                   str(plugin.get_description()), str(plugin.get_machine_oriented()),
                                   str(plugin.get_modify_date()), str(plugin.get_name()),
                                   str(plugin.get_policy_plugin()),
                                   str(plugin.get_user_oriented()), str(plugin.get_version()),
                                   str(plugin.get_task_plugin()), str(plugin.get_x_based())]
                    plugin_id = self.db_service.update('plugin', plugin_columns, plugin_args)

                    profile_args = [str(ahenk_policy_id), str(profile.get_create_date()),
                                    str(profile.get_modify_date()),
                                    str(profile.get_label()), str(profile.get_description()),
                                    str(profile.get_overridable()), str(profile.get_active()),
                                    str(profile.get_deleted()),
                                    str(profile.get_profile_data()), plugin_id]
                    self.db_service.update('profile', profile_columns, profile_args)

            elif ahenk_policy_ver:
                self.logger.debug('Already there is ahenk policy. Command Execution Id is updating')
                self.db_service.update('policy', ['execution_id'], [policy.get_agent_execution_id()], 'type = \'A\'')
            else:
                self.logger.debug('There is no any Ahenk policy.')

            if policy.get_user_policy_version() != user_policy_version:
                user_policy_id = self.db_service.select_one_result('policy', 'id',
                                                                   'type = \'U\' and name=\'' + policy.get_username() + '\'')
                if user_policy_id is not None:
                    # TODO remove profiles' plugins
                    self.db_service.delete('profile', 'id=' + str(user_policy_id))
                    self.db_service.delete('plugin', 'id=' + str(user_policy_id))
                    self.db_service.update('policy', ['version', 'execution_id', 'expiration_date'],
                                           [str(policy.get_user_policy_version()), policy.user_execution_id,
                                            str(policy.user_expiration_date)],
                                           'type=\'U\' and name=\'' + policy.get_username() + '\'')
                else:
                    self.db_service.update('policy', ['type', 'version', 'name', 'execution_id', 'expiration_date'],
                                           ['U', str(policy.get_user_policy_version()), policy.get_username(),
                                            policy.get_user_execution_id(), policy.user_expiration_date])
                    user_policy_id = self.db_service.select_one_result('policy', 'id',
                                                                       'type = \'U\' and name=\'' + policy.get_username() + '\'')

                for profile in policy.get_user_profiles():
                    plugin = profile.get_plugin()

                    plugin_args = [str(plugin.get_active()), str(plugin.get_create_date()), str(plugin.get_deleted()),
                                   str(plugin.get_description()), str(plugin.get_machine_oriented()),
                                   str(plugin.get_modify_date()), str(plugin.get_name()),
                                   str(plugin.get_policy_plugin()),
                                   str(plugin.get_user_oriented()), str(plugin.get_version()),
                                   str(plugin.get_task_plugin()), str(plugin.get_x_based())]
                    plugin_id = self.db_service.update('plugin', plugin_columns, plugin_args)

                    profile_args = [str(user_policy_id), str(profile.get_create_date()), str(profile.get_modify_date()),
                                    str(profile.get_label()), str(profile.get_description()),
                                    str(profile.get_overridable()), str(profile.get_active()),
                                    str(profile.get_deleted()),
                                    str(profile.get_profile_data()), plugin_id]
                    self.db_service.update('profile', profile_columns, profile_args)

            elif user_policy_version:
                self.logger.debug('Already there is user policy. . Command Execution Id is updating')
                self.db_service.update('policy', ['execution_id'], [policy.get_user_execution_id()], 'type = \'U\'')
            else:
                self.logger.debug('There is no any user policy')

            policy = self.get_active_policies(policy.get_username())
            # TODO check is null
            self.task_manager.addPolicy(policy)
        except Exception as e:
            self.logger.error('A problem occurred while executing policy. Erroe Message: {0}:'.format(str(e)))

    def check_expiration(self, expiration):
        current_timestamp = int(time.time()) * 1000
        if str(expiration) =='None':
            return True
        elif int(expiration) > current_timestamp:
            return True
        else:
            return False

    def get_active_policies(self, username):

        try:
            # TODO vt den gecerli son tarihi olani cek
            user_policy = self.db_service.select('policy', ['id', 'version', 'name', 'expiration_date'],
                                                 ' type=\'U\' and name=\'' + username + '\'')
            ahenk_policy = self.db_service.select('policy', ['id', 'version', 'expiration_date'], ' type=\'A\' ')

            plugin_columns = ['id', 'active', 'create_date', 'deleted', 'description', 'machine_oriented',
                              'modify_date',
                              'name', 'policy_plugin', 'user_oriented', 'version', 'task_plugin', 'x_based']
            profile_columns = ['id', 'create_date', 'label', 'description', 'overridable', 'active', 'deleted',
                               'profile_data', 'modify_date', 'plugin']

            policy = PolicyBean(username=username)

            if len(user_policy) > 0 and self.check_expiration(user_policy[0][3]):
                user_policy_version = user_policy[0][0]
                policy.set_user_policy_version(user_policy_version)

                user_profiles = self.db_service.select('profile', profile_columns,
                                                       ' id=' + str(user_policy_version) + ' ')
                arr_profiles = []
                if len(user_profiles) > 0:
                    for profile in user_profiles:
                        plu = self.db_service.select('plugin', plugin_columns, ' id=\'' + profile[9] + '\'')[0]
                        plugin = PluginBean(p_id=plu[0], active=plu[1], create_date=plu[2], deleted=plu[3],
                                            description=plu[4], machine_oriented=plu[5], modify_date=plu[6],
                                            name=plu[7],
                                            policy_plugin=plu[8], user_oriented=plu[9], version=plu[10],
                                            task_plugin=plu[11], x_based=plu[12])

                        arr_profiles.append(
                            ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5],
                                        profile[6],
                                        profile[7], profile[8], plugin, policy.get_username()))
                    policy.set_user_profiles(arr_profiles)

            if len(ahenk_policy) > 0 and self.check_expiration(ahenk_policy[0][2]):
                ahenk_policy_version = ahenk_policy[0][0]
                policy.set_ahenk_policy_version(ahenk_policy_version)
                ahenk_profiles = self.db_service.select('profile', profile_columns,
                                                        ' id=' + str(ahenk_policy_version) + ' ')
                arr_profiles = []
                if len(ahenk_profiles) > 0:
                    for profile in ahenk_profiles:
                        plu = self.db_service.select('plugin', plugin_columns, ' id=\'' + profile[9] + '\'')[0]
                        plugin = PluginBean(p_id=plu[0], active=plu[1], create_date=plu[2], deleted=plu[3],
                                            description=plu[4], machine_oriented=plu[5], modify_date=plu[6],
                                            name=plu[7],
                                            policy_plugin=plu[8], user_oriented=plu[9], version=plu[10],
                                            task_plugin=plu[11], x_based=plu[12])

                        arr_profiles.append(
                            ProfileBean(profile[0], profile[1], profile[2], profile[3], profile[4], profile[5],
                                        profile[6],
                                        profile[7], profile[8], plugin, policy.get_username()))
                    policy.set_ahenk_profiles(arr_profiles)

            return policy
        except Exception as e:
            self.logger.error('A problem occurred while getting active policies. Error Message : {0}'.format(str(e)))

    def execute_task(self, arg):

        json_task = json.loads(arg)['task']
        json_task = json.loads(json_task)
        json_server_conf = json.dumps(json.loads(arg)['fileServerConf'])

        task = self.json_to_task_bean(json_task, json_server_conf)
        self.logger.debug('Adding new  task...Task is:{0}'.format(task.get_command_cls_id()))

        self.task_manager.addTask(task)
        self.logger.debug('Task added')

    def unregister(self, msg):
        j = json.loads(msg)
        status = str(j['status']).lower()

        if 'not_authorized' == str(status):
            self.logger.info('Registration is failed. User not authorized')
            Util.show_message('Ahenk etki alanından çıkarmak için yetkili kullanıcı haklarına sahip olmanız gerekmektedir.',
                   'Kullanıcı Yetkilendirme Hatası')
        else :
            registration= Scope.get_instance().get_registration()
            registration.purge_and_unregister()


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

    def execute_script(self, arg):
        try:
            self.logger.debug('Executing script...')
            messenger = Scope().get_instance().get_messenger()

            json_data = json.loads(arg)
            result_code, p_out, p_err = Util.execute(str(json_data['command']))

            self.logger.debug('Executed script')

            data = dict()
            data['type'] = 'SCRIPT_RESULT'
            data['timestamp'] = str(Util.timestamp())

            if result_code == 0:
                self.logger.debug('Command execution was finished successfully')
                try:
                    temp_name = str(Util.generate_uuid())
                    temp_full_path = System.Ahenk.received_dir_path() + temp_name
                    self.logger.debug('Writing result to file')
                    Util.write_file(temp_full_path, str(p_out))
                    md5 = Util.get_md5_file(temp_full_path)
                    Util.rename_file(temp_full_path, System.Ahenk.received_dir_path() + md5)

                    file_manager = FileTransferManager(json_data['fileServerConf']['protocol'],
                                                       json_data['fileServerConf']['parameterMap'])
                    file_manager.transporter.connect()
                    self.logger.debug('File transfer connection was created')
                    success = file_manager.transporter.send_file(System.Ahenk.received_dir_path() + md5, md5)
                    self.logger.debug('File was transferred')
                    file_manager.transporter.disconnect()
                    self.logger.debug('File transfer connection was closed')

                    if success is False:
                        self.logger.error('A problem occurred while file transferring')
                        data['resultCode'] = '-1'
                        data[
                            'errorMessage'] = 'Command executed successfully but a problem occurred while sending result file'

                    else:
                        data['md5'] = md5

                except Exception as e:
                    self.logger.error(
                        'A problem occurred while file transferring. Error Message :{0}'.format(
                            str(e)))
                    raise
            else:
                self.logger.error(
                    'Command execution was failed. Error Message :{0}'.format(str(result_code)))
                data['resultCode'] = str(result_code)
                data['errorMessage'] = str(p_err)

            messenger.send_direct_message(json.dumps(data))
        except Exception as e:
            self.logger.error(
                'A problem occurred while running execute script action. Error Message :{0}'.format(
                    str(e)))

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
                          user_execution_id=json_data['userCommandExecutionId'],
                          agent_expiration_date=json_data['agentPolicyExpirationDate'],
                          user_expiration_date=json_data['userPolicyExpirationDate'])
