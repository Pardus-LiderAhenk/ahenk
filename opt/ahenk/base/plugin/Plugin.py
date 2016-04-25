#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import subprocess
import threading

from base.Scope import Scope
from base.model.MessageType import MessageType
from base.model.Response import Response


class Context(object):
    def __init__(self):
        self.data = {}
        self.scope = Scope().getInstance()
        self.logger = self.scope.getLogger()
        self.config_manager = self.scope.getConfigurationManager()

    def debug(self, message):
        self.logger.debug('[PLUGIN]' + message)

    def info(self, message):
        self.logger.info('[PLUGIN]' + message)

    def error(self, message):
        self.logger.error('[PLUGIN]' + message)

    def put(self, var_name, data):
        self.data[var_name] = data

    def get(self, var_name):
        return self.data[var_name]

    def empty_data(self):
        self.data = {}

    def execute(self, command):
        return subprocess.Popen(command, shell=True)

    def get_path(self):
        return self.config_manager.get('PLUGIN', 'pluginfolderpath')

        # TODO send file,...


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
        self.messager = None

        self.keep_run = True
        self.context = Context()

    def run(self):

        while self.keep_run:
            try:
                item_obj = self.InQueue.get(block=True)
                obj_name = item_obj.obj_name
                if obj_name == "TASK":
                    command = Scope.getInstance().getPluginManager().findCommand(self.getName(), item_obj.get_command_cls_id().lower())
                    command.handle_task(item_obj, self.context)
                    # TODO create response message from context and item_obj. item_obj is task

                    response = Response(type=MessageType.TASK_STATUS.value, id=item_obj.get_id(), code=self.context.get('responseCode'), message=self.context.get('responseMessage'), data=self.context.get('responseData'), content_type=self.context.get('contentType'))
                    # self.response_queue.put(self.messaging.response_msg(response)) #TODO DEBUG
                    Scope.getInstance().getMessager().send_direct_message(self.messaging.task_status_msg(response))  # TODO REMOVE

                    # Empty context for next use
                    self.context.empty_data()

                elif obj_name == "PROFILE":
                    profile_data = item_obj.get_profile_data()
                    policy_module = Scope.getInstance().getPluginManager().findPolicyModule(item_obj.get_plugin().get_name())
                    self.context.put('username', item_obj.get_username())
                    policy_module.handle_policy(profile_data, self.context)

                    execution_id = self.get_execution_id(item_obj.get_id())
                    policy_ver = self.get_policy_version(item_obj.get_id())

                    response = Response(type=MessageType.POLICY_STATUS.value, id=item_obj.get_id(), code=self.context.get('responseCode'), message=self.context.get('responseMessage'), data=self.context.get('responseData'), content_type=self.context.get('contentType'), execution_id=execution_id, policy_version=policy_ver)
                    # self.response_queue.put(self.messaging.response_msg(response)) #TODO DEBUG
                    Scope.getInstance().getMessager().send_direct_message(self.messaging.policy_status_msg(response))  # TODO REMOVE

                    # Empty context for next use
                    self.context.empty_data()

                elif obj_name == "KILL_SIGNAL":
                    self.keep_run = False
                    self.logger.debug('[Plugin] Killing queue ! Plugin Name : ' + str(self.name))
                elif obj_name == "SAFE_MODE":
                    username = item_obj.username
                    safe_mode_module = Scope.getInstance().getPluginManager().find_safe_mode_module(self.name)
                    safe_mode_module.handle_safe_mode(username, self.context)
                    self.context.empty_data()
                else:
                    self.logger.warning("[Plugin] Not supported object type " + obj_name)
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
