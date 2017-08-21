#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import threading
import ast
from base.file.file_transfer_manager import FileTransferManager
from base.model.enum.content_type import ContentType
from base.model.enum.message_code import MessageCode
from base.model.enum.message_type import MessageType
from base.model.response import Response
from base.scope import Scope
from base.system.system import System
from base.util.util import Util


class Context(object):
    def __init__(self):
        self.data = dict()
        self.scope = Scope().get_instance()
        self.mail_send = False
        self.mail_subject = ''
        self.mail_content = ''

    def put(self, var_name, data):
        self.data[var_name] = data

    def get(self, var_name):
        return self.data[var_name]

    def get_username(self):
        return self.data['username']

    def empty_data(self):
        self.data = dict()

    def create_response(self, code, message=None, data=None, content_type=None):
        self.data['responseCode'] = code
        self.data['responseMessage'] = message
        self.data['responseData'] = data
        self.data['contentType'] = content_type

    def fetch_file(self, remote_path, local_path=None, file_name=None):
        success = None
        try:
            custom_map = self.get('parameterMap')
            custom_map['path'] = remote_path
            file_manager = FileTransferManager(self.get('protocol'), custom_map)
            file_manager.transporter.connect()
            success = file_manager.transporter.get_file(local_path, file_name)
            file_manager.transporter.disconnect()
        except Exception as e:
            raise

        return success

    def is_mail_send(self):
        return self.mail_send

    def set_mail_send(self, mail_send):
        self.mail_send=mail_send

    def get_mail_subject(self):
        return self.mail_subject

    def set_mail_subject(self, mail_subject):
        self.mail_subject=mail_subject

    def get_mail_content(self):
        return self.mail_content

    def set_mail_content(self, mail_content):
        self.mail_content = mail_content


class Plugin(threading.Thread):
    """
        This is a thread inherit class and have a queue.
        Plugin class responsible for processing TASK or USER PLUGIN PROFILE.
    """

    def __init__(self, name, in_ueue):
        threading.Thread.__init__(self)
        self.name = name
        self.in_queue = in_ueue

        scope = Scope.get_instance()
        self.logger = scope.get_logger()
        self.response_queue = scope.get_response_queue()
        self.messaging = scope.get_message_manager()
        self.db_service = scope.get_db_service()

        self.keep_run = True
        self.context = Context()

    def run(self):

        while self.keep_run:
            try:
                try:
                    item_obj = self.in_queue.get(block=True)
                    obj_name = item_obj.obj_name
                except Exception as e:
                    self.logger.error(
                        '[Plugin] A problem occurred while executing process. Error Message: {0}'.format(str(e)))

                if obj_name == "TASK":
                    self.logger.debug('[Plugin] Executing task')
                    self.context.put('task_id', item_obj.get_id())

                    if item_obj.get_file_server() is not None and item_obj.get_file_server() != 'null':
                        self.context.put('protocol', json.loads(item_obj.get_file_server())['protocol'])
                        self.context.put('parameterMap', json.loads(item_obj.get_file_server())['parameterMap'])

                    if type(item_obj.get_parameter_map())==str:
                        task_data = json.loads(item_obj.get_parameter_map())
                    elif type(item_obj.get_parameter_map())==dict:
                        task_data = item_obj.get_parameter_map()

                    # check if mail send is actve or not and set mail params to context object.. plugins get mail params via context object
                    self.context.set_mail_send(task_data['mailSend'] if 'mailSend' in task_data else False)
                    self.context.set_mail_subject(task_data['mailSubject'] if 'mailSubject' in task_data else '')
                    self.context.set_mail_content(task_data['mailContent'] if 'mailContent' in task_data else '')

                    self.logger.debug('[Plugin] Sending notify to user about task process')

                    if System.Sessions.user_name() is not None and len(System.Sessions.user_name()) > 0:
                        for user in System.Sessions.user_name():
                            Util.send_notify("Lider Ahenk",
                                             "{0} eklentisi şu anda bir görev çalıştırıyor.".format(self.getName()),
                                             System.Sessions.display(user),
                                             user)
                    self.context.put('taskData', task_data)
                    self.context.put('taskId', item_obj.get_id())

                    self.logger.debug('[Plugin] Handling task')
                    Scope.get_instance().get_plugin_manager().find_command(self.getName(),
                                                                           item_obj.get_plugin().get_version(),
                                                                           item_obj.get_command_cls_id().lower()).handle_task(ast.literal_eval(str(task_data)), self.context)


                    if self.context.data is not None and self.context.get('responseCode') is not None:
                        self.logger.debug('[Plugin] Creating response')
                        response = Response(type=MessageType.TASK_STATUS.value, id=item_obj.get_id(),
                                             code=self.context.get('responseCode'),
                                            message=self.context.get('responseMessage'),
                                            data=self.context.get('responseData'),
                                            content_type=self.context.get('contentType'))

                        if response.get_data() and response.get_content_type() != ContentType.APPLICATION_JSON.value:
                            success = False
                            try:
                                file_manager = FileTransferManager(json.loads(item_obj.get_file_server())['protocol'],
                                                                   json.loads(item_obj.get_file_server())[
                                                                       'parameterMap'])
                                file_manager.transporter.connect()
                                md5 = str(json.loads(response.get_data())['md5'])
                                success = file_manager.transporter.send_file(System.Ahenk.received_dir_path() + md5,
                                                                             md5)
                                file_manager.transporter.disconnect()
                            except Exception as e:
                                self.logger.error(
                                    '[Plugin] A problem occurred while file transferring. Error Message :{0}'.format(
                                        str(e)))

                            self.logger.debug('[Plugin] Sending response')

                            message = self.messaging.task_status_msg(response)
                            if success is False:
                                response = Response(type=MessageType.TASK_STATUS.value, id=item_obj.get_id(),
                                                    code=MessageCode.TASK_ERROR.value,
                                                    message='Task processed successfully but file transfer not completed. Check defined server conf')
                                message = self.messaging.task_status_msg(response)

                            Scope.get_instance().get_messenger().send_direct_message(message)

                        else:
                            self.logger.debug('[Plugin] Sending task response')
                            Scope.get_instance().get_messenger().send_direct_message(
                                self.messaging.task_status_msg(response))

                    else:
                        self.logger.error(
                            '[Plugin] There is no Response. Plugin must create response after run a task!')

                elif obj_name == "PROFILE":

                    self.logger.debug('[Plugin] Executing profile')
                    profile_data = item_obj.get_profile_data()
                    self.context.put('username', item_obj.get_username())

                    json_profile_data=json.loads(profile_data)
                    self.context.set_mail_send(json_profile_data['mailSend'] if 'mailSend' in json_profile_data else False)
                    self.context.set_mail_subject(json_profile_data['mailSubject'] if 'mailSubject' in json_profile_data else '')
                    self.context.set_mail_content(json_profile_data['mailContent'] if 'mailContent' in json_profile_data else '')


                    execution_id = self.get_execution_id(item_obj.get_id())
                    policy_ver = self.get_policy_version(item_obj.get_id())

                    self.context.put('policy_version', policy_ver)
                    self.context.put('execution_id', execution_id)

                    # if item_obj.get_file_server() is not None  and item_obj.get_file_server() !='null':
                    #     self.context.put('protocol', json.loads(item_obj.get_file_server())['protocol'])
                    #     self.context.put('parameterMap', json.loads(item_obj.get_file_server())['parameterMap'])

                    self.logger.debug('[Plugin] Sending notify to user about profile process')

                    Util.send_notify("Lider Ahenk",
                                     "{0} eklentisi şu anda bir profil çalıştırıyor.".format(self.getName()),
                                     System.Sessions.display(item_obj.get_username()),
                                     item_obj.get_username())
                    self.logger.debug('[Plugin] Handling profile')
                    Scope.get_instance().get_plugin_manager().find_policy_module(item_obj.get_plugin().get_name()).handle_policy(profile_data, self.context)

                    if self.context.data is not None and self.context.get('responseCode') is not None:
                        self.logger.debug('[Plugin] Creating response')
                        response = Response(type=MessageType.POLICY_STATUS.value, id=item_obj.get_id(),
                                            code=self.context.get('responseCode'),
                                            message=self.context.get('responseMessage'),
                                            data=self.context.get('responseData'),
                                            content_type=self.context.get('contentType'), execution_id=execution_id,
                                            policy_version=policy_ver)

                        if response.get_data() and response.get_content_type() != ContentType.APPLICATION_JSON.value:
                            success = False
                            try:
                                file_manager = FileTransferManager(json.loads(item_obj.get_file_server())['protocol'],
                                                                   json.loads(item_obj.get_file_server())[
                                                                       'parameterMap'])
                                file_manager.transporter.connect()
                                md5 = str(json.loads(response.get_data())['md5'])
                                success = file_manager.transporter.send_file(System.Ahenk.received_dir_path() + md5,
                                                                             md5)
                                file_manager.transporter.disconnect()
                            except Exception as e:
                                self.logger.error(
                                    '[Plugin] A problem occurred while file transferring. Error Message :{0}'.format(
                                        str(e)))

                            self.logger.debug('[Plugin] Sending response')

                            message = self.messaging.task_status_msg(response)
                            if success is False:
                                response = Response(type=MessageType.POLICY_STATUS.value, id=item_obj.get_id(),
                                                    code=MessageCode.POLICY_ERROR.value,
                                                    message='Policy processed successfully but file transfer not completed. Check defined server conf')
                                message = self.messaging.task_status_msg(response)
                            Scope.get_instance().get_messenger().send_direct_message(message)
                        else:
                            self.logger.debug('[Plugin] Sending profile response')
                            Scope.get_instance().get_messenger().send_direct_message(
                                self.messaging.policy_status_msg(response))
                    else:
                        self.logger.error(
                            '[Plugin] There is no Response. Plugin must create response after run a policy!')
                elif 'MODE' in obj_name:
                    module = Scope.get_instance().get_plugin_manager().find_module(obj_name, self.name)
                    if module is not None:
                        if item_obj.obj_name in ('LOGIN_MODE', 'LOGOUT_MODE', 'SAFE_MODE'):
                            self.context.put('username', item_obj.username)
                        try:
                            self.logger.debug(
                                '[Plugin] {0} is running on {1} plugin'.format(str(item_obj.obj_name), str(self.name)))
                            module.handle_mode(self.context)
                        except Exception as e:
                            self.logger.error(
                                '[Plugin] A problem occurred while running {0} on {1} plugin. Error Message: {2}'.format(
                                    str(obj_name), str(self.name), str(e)))

                    if item_obj.obj_name is 'SHUTDOWN_MODE':
                        self.logger.debug('[Plugin] {0} plugin is stopping...'.format(str(self.name)))
                        self.keep_run = False
                else:
                    self.logger.warning("[Plugin] Not supported object type: {0}".format(str(obj_name)))

                self.context.empty_data()
            except Exception as e:
                self.logger.error("[Plugin] Plugin running exception. Exception Message: {0} ".format(str(e)))

    def get_execution_id(self, profile_id):
        try:
            return self.db_service.select_one_result('policy', 'execution_id', ' id={0}'.format(profile_id))
        except Exception as e:
            self.logger.error(
                "[Plugin] A problem occurred while getting execution id. Exception Message: {0} ".format(str(e)))
            return None

    def get_policy_version(self, profile_id):
        try:
            return self.db_service.select_one_result('policy', 'version', ' id={0}'.format(profile_id))
        except Exception as e:
            self.logger.error(
                "[Plugin] A problem occurred while getting policy version . Exception Message: {0} ".format(str(e)))
            return None

    def getName(self):
        return self.name
