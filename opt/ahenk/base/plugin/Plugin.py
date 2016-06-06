#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import threading

from base.Scope import Scope
from base.model.Response import Response
from base.model.enum.MessageType import MessageType


class Context(object):
    def __init__(self):
        self.data = {}
        self.scope = Scope().getInstance()

    def put(self, var_name, data):
        self.data[var_name] = data

    def get(self, var_name):
        return self.data[var_name]

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

                    self.logger.debug('[Plugin] Creating response')

                    if self.context.get('responseCode') is not None:
                        response = Response(type=MessageType.TASK_STATUS.value, id=item_obj.get_id(), code=self.context.get('responseCode'), message=self.context.get('responseMessage'), data=self.context.get('responseData'), content_type=self.context.get('contentType'))
                        # self.response_queue.put(self.messaging.response_msg(response)) #TODO DEBUG
                        self.logger.debug('[Plugin] Sending response')
                        Scope.getInstance().getMessager().send_direct_message(self.messaging.task_status_msg(response))  # TODO REMOVE
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

                    if self.context.get('responseCode') is not None:
                        self.logger.debug('[Plugin] Creating response')
                        response = Response(type=MessageType.POLICY_STATUS.value, id=item_obj.get_id(), code=self.context.get('responseCode'), message=self.context.get('responseMessage'), data=self.context.get('responseData'), content_type=self.context.get('contentType'), execution_id=execution_id, policy_version=policy_ver)
                        # self.response_queue.put(self.messaging.response_msg(response)) #TODO DEBUG
                        self.logger.debug('[Plugin] Sending response')
                        Scope.getInstance().getMessager().send_direct_message(self.messaging.policy_status_msg(response))  # TODO REMOVE
                    else:
                        self.logger.error('[Plugin] There is no Response. Plugin must create response after run a policy!')

                elif obj_name == "KILL_SIGNAL":
                    self.keep_run = False
                    self.logger.debug('[Plugin] Killing queue ! Plugin Name: {}'.format(str(self.name)))
                elif obj_name == "SAFE_MODE":
                    username = item_obj.username
                    safe_mode_module = Scope.getInstance().getPluginManager().find_safe_mode_module(self.name)
                    safe_mode_module.handle_safe_mode(username, self.context)
                else:
                    self.logger.warning("[Plugin] Not supported object type: {}".format(str(obj_name)))

                # Empty context for next use
                self.context.empty_data()
            except Exception as e:
                self.logger.error("[Plugin] Plugin running exception. Exception Message: {} ".format(str(e)))

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
