#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>


class Scope(object):
    """docstring for Scope"""

    scope_instance = None

    def __init__(self):
        super(Scope, self).__init__()
        self.custom_map = dict()
        self.configuration_manager = None
        self.message_manager = None
        self.logger = None
        self.plugin_manager = None
        self.task_manager = None
        self.response_queue = None
        self.registration = None
        self.event_manager = None
        self.execution_manager = None
        self.db_service = None
        self.messenger = None
        self.scheduler = None

    @staticmethod
    def get_instance():
        return scope_instance

    @staticmethod
    def set_instance(scope_obj):
        global scope_instance
        scope_instance = scope_obj

    def get_custom_map(self):
        return self.custom_map

    def put_custom_map(self, name, value):
        self.custom_map[str(name)] = value

    def get_custom_param(self, name):
        return self.custom_map[str(name)]

    def get_configuration_manager(self):
        return self.configuration_manager

    def set_configuration_manager(self, configuration_manager):
        self.configuration_manager = configuration_manager

    def get_logger(self):
        return self.logger

    def set_logger(self, logger):
        self.logger = logger

    def get_message_manager(self):
        return self.message_manager

    def set_message_manager(self, message_manager):
        self.message_manager = message_manager

    def get_plugin_manager(self):
        return self.plugin_manager

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def get_task_manager(self):
        return self.task_manager

    def set_task_manager(self, task_manager):
        self.task_manager = task_manager

    def get_response_queue(self):
        return self.response_queue

    def set_response_queue(self, response_queue):
        self.response_queue = response_queue

    def get_registration(self):
        return self.registration

    def set_registration(self, registration):
        self.registration = registration

    def get_event_manager(self):
        return self.event_manager

    def set_event_manager(self, event_manager):
        self.event_manager = event_manager

    def get_execution_manager(self):
        return self.execution_manager

    def set_execution_manager(self, execution_manager):
        self.execution_manager = execution_manager

    def get_db_service(self):
        return self.db_service

    def set_sb_service(self, db_service):
        self.db_service = db_service

    def get_messenger(self):
        return self.messenger

    def set_messenger(self, messenger):
        self.messenger = messenger

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def get_scheduler(self):
        return self.scheduler
