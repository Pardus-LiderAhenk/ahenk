#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import threading
import json
from base.Scope import Scope
from base.model.Response import Response
from base.file.file_transfer_manager import FileTransferManager
from base.model.enum.MessageType import MessageType
from base.model.enum.MessageCode import MessageCode
from base.model.enum.ContentType import ContentType
from base.system.system import System


class Context(object):
    def __init__(self):
        self.data = {}
        self.scope = Scope().getInstance()

    def put(self, var_name, data):
        self.data[var_name] = data

    def get(self, var_name):
        return self.data[var_name]

    def get_username(self):
        return self.data['username']

    def empty_data(self):
        self.data = {}

    def create_response(self, code, message=None, data=None, content_type=None):
        self.data['responseCode'] = code
        self.data['responseMessage'] = message
        self.data['responseData'] = data
        self.data['contentType'] = content_type


class Plugin(threading.Thread):
    """
        This is a thread inherit class and have a queue.
        Plugin class responsible for processing TASK or USER PLUGIN PROFILE.
    """

    def __init__(self, name, InQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.InQueue = InQueue

        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.response_queue = scope.getResponseQueue()
        self.messaging = scope.getMessageManager()
        self.db_service = scope.getDbService()
        # self.messager = None

        self.keep_run = True
        self.context = Context()

    def run(self):

        while self.keep_run:
            try:
                try:
                    item_obj = self.InQueue.get(block=True)
                    obj_name = item_obj.obj_name
                except Exception as e:
                    self.logger.error('[Plugin] A problem occurred while executing process. Error Message: {}'.format(str(e)))

                if obj_name == "TASK":
                    self.logger.debug('[Plugin] Executing task')
                    command = Scope.getInstance().getPluginManager().findCommand(self.getName(), item_obj.get_command_cls_id().lower())
                    self.context.put('task_id', item_obj.get_command_cls_id().lower())

                    task_data = item_obj.get_parameter_map()
                    self.logger.debug('[Plugin] Handling task')
                    command.handle_task(task_data, self.context)

                    if self.context.data is not None and self.context.get('responseCode') is not None:
                        self.logger.debug('[Plugin] Creating response')
                        response = Response(type=MessageType.TASK_STATUS.value, id=item_obj.get_id(), code=self.context.get('responseCode'), message=self.context.get('responseMessage'), data=self.context.get('responseData'), content_type=self.context.get('contentType'))

                        if response.get_data() and response.get_content_type() != ContentType.APPLICATION_JSON.value:
                            success = False
                            try:
                                file_manager = FileTransferManager(json.loads(item_obj.get_file_server())['protocol'], json.loads(item_obj.get_file_server())['parameterMap'])
                                file_manager.transporter.connect()
                                md5 = str(json.loads(response.get_data())['md5'])
                                success = file_manager.transporter.send_file(System.Ahenk.received_dir_path() + md5, md5)
                                file_manager.transporter.disconnect()
                            except Exception as e:
                                self.logger.error('[Plugin] A problem occurred while file transferring. Error Message :{}'.format(str(e)))

                            self.logger.debug('[Plugin] Sending response')

                            message = self.messaging.task_status_msg(response)
                            if success is False:
                                response = Response(type=MessageType.TASK_STATUS.value, id=item_obj.get_id(), code=MessageCode.TASK_ERROR.value, message='[Ahenk Core] Task processed successfully but file transfer not completed. Check defined server conf')
                                message = self.messaging.task_status_msg(response)

                            Scope.getInstance().getMessenger().send_direct_message(message)

                        else:
                            self.logger.debug('[Plugin] Sending task response')
                            Scope.getInstance().getMessenger().send_direct_message(self.messaging.task_status_msg(response))

                    else:
                        self.logger.error('[Plugin] There is no Response. Plugin must create response after run a task!')

                elif obj_name == "PROFILE":

                    self.logger.debug('[Plugin] Executing profile')
                    profile_data = item_obj.get_profile_data()
                    policy_module = Scope.getInstance().getPluginManager().findPolicyModule(item_obj.get_plugin().get_name())
                    self.context.put('username', item_obj.get_username())

                    execution_id = self.get_execution_id(item_obj.get_id())
                    policy_ver = self.get_policy_version(item_obj.get_id())

                    self.context.put('policy_version', policy_ver)
                    self.context.put('execution_id', execution_id)

                    self.logger.debug('[Plugin] Handling profile')
                    policy_module.handle_policy(profile_data, self.context)

                    if self.context.data is not None and self.context.get('responseCode') is not None:
                        self.logger.debug('[Plugin] Creating response')
                        response = Response(type=MessageType.POLICY_STATUS.value, id=item_obj.get_id(), code=self.context.get('responseCode'), message=self.context.get('responseMessage'), data=self.context.get('responseData'), content_type=self.context.get('contentType'), execution_id=execution_id, policy_version=policy_ver)

                        if response.get_data() and response.get_content_type() != ContentType.APPLICATION_JSON.value:
                            success = False
                            try:
                                file_manager = FileTransferManager(json.loads(item_obj.get_file_server())['protocol'], json.loads(item_obj.get_file_server())['parameterMap'])
                                file_manager.transporter.connect()
                                md5 = str(json.loads(response.get_data())['md5'])
                                success = file_manager.transporter.send_file(System.Ahenk.received_dir_path() + md5, md5)
                                file_manager.transporter.disconnect()
                            except Exception as e:
                                self.logger.error('[Plugin] A problem occurred while file transferring. Error Message :{}'.format(str(e)))

                            self.logger.debug('[Plugin] Sending response')

                            message = self.messaging.task_status_msg(response)
                            if success is False:
                                response = Response(type=MessageType.POLICY_STATUS.value, id=item_obj.get_id(), code=MessageCode.POLICY_ERROR.value, message='[Ahenk Core] Policy processed successfully but file transfer not completed. Check defined server conf')
                                message = self.messaging.task_status_msg(response)
                            Scope.getInstance().getMessenger().send_direct_message(message)
                        else:
                            self.logger.debug('[Plugin] Sending profile response')
                            Scope.getInstance().getMessenger().send_direct_message(self.messaging.policy_status_msg(response))
                    else:
                        self.logger.error('[Plugin] There is no Response. Plugin must create response after run a policy!')
                elif obj_name == "KILL_SIGNAL":
                    self.keep_run = False
                    self.logger.debug('[Plugin] Killing queue ! Plugin Name: {}'.format(str(self.name)))
                elif 'MODE' in obj_name:
                    module = Scope.getInstance().getPluginManager().find_module(obj_name, self.name)
                    if module is not None:
                        if item_obj.obj_name in ('LOGIN_MODE', 'LOGOUT_MODE', 'SAFE_MODE'):
                            self.context.put('username', item_obj.username)
                        try:
                            self.logger.debug('[Plugin] {0} is running on {1} plugin'.format(str(item_obj.obj_name), str(self.name)))
                            module.handle_mode(self.context)
                        except Exception as e:
                            self.logger.error('[Plugin] A problem occurred while running {0} on {1} plugin. Error Message: {2}'.format(str(obj_name), str(self.name), str(e)))

                    if item_obj.obj_name is 'SHUTDOWN_MODE':
                        self.logger.debug('[Plugin] {0} plugin is stopping...'.format(str(self.name)))
                        self.keep_run = False
                else:
                    self.logger.warning("[Plugin] Not supported object type: {}".format(str(obj_name)))

                self.context.empty_data()
            except Exception as e:
                self.logger.error("[Plugin] Plugin running exception about {0}. Exception Message: {1} ".format(obj_name, str(e)))

    def get_execution_id(self, profile_id):
        try:
            return self.db_service.select_one_result('policy', 'execution_id', ' id={}'.format(profile_id))
        except Exception as e:
            self.logger.error("[Plugin] A problem occurred while getting execution id. Exception Message: {} ".format(str(e)))
            return None

    def get_policy_version(self, profile_id):
        try:
            return self.db_service.select_one_result('policy', 'version', ' id={}'.format(profile_id))
        except Exception as e:
            self.logger.error("[Plugin] A problem occurred while getting policy version . Exception Message: {} ".format(str(e)))
            return None

    def getName(self):
        return self.name
