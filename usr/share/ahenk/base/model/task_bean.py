#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>


class TaskBean(object):
    """docstring for TaskBean"""

    def __init__(self, _id=None, create_date=None, modify_date=None, command_cls_id=None, parameter_map=None, deleted=None, plugin=None, cron_str=None, file_server=None):
        self._id = _id
        self.create_date = create_date
        self.modify_date = modify_date
        self.command_cls_id = command_cls_id
        self.parameter_map = parameter_map
        self.deleted = deleted
        self.plugin = plugin
        self.cron_str = cron_str
        self.file_server = file_server

    def get_id(self):
        return self._id

    def set_id(self, _id):
        self._id = _id

    def get_create_date(self):
        return self.create_date

    def set_create_date(self, create_date):
        self.create_date = create_date

    def get_modify_date(self):
        return self.modify_date

    def set_modify_date(self, modify_date):
        self.modify_date = modify_date

    def get_command_cls_id(self):
        return self.command_cls_id

    def set_command_cls_id(self, command_cls_id):
        self.command_cls_id = command_cls_id

    def get_parameter_map(self):
        return self.parameter_map

    def set_parameter_map(self, parameter_map):
        self.parameter_map = parameter_map

    def get_deleted(self):
        return self.deleted

    def set_deleted(self, deleted):
        self.deleted = deleted

    def get_plugin(self):
        return self.plugin

    def set_plugin(self, plugin):
        self.plugin = plugin

    def get_cron_str(self):
        return self.cron_str

    def set_cron_str(self, cron_str):
        self.cron_str = cron_str

    def get_file_server(self):
        return self.file_server

    def set_file_server(self, file_server):
        self.file_server = file_server

    def to_json(self):
        plugin_data = dict()
        plugin_data['id'] = self.plugin.get_id()
        plugin_data['name'] = self.plugin.get_name()
        plugin_data['version'] = self.plugin.get_version()
        plugin_data['description'] = self.plugin.get_description()
        plugin_data['active'] = self.plugin.get_active()
        plugin_data['deleted'] = self.plugin.get_deleted()
        plugin_data['machineOriented'] = self.plugin.get_machine_oriented()
        plugin_data['userOriented'] = self.plugin.get_user_oriented()
        plugin_data['policyPlugin'] = self.plugin.get_policy_plugin()
        plugin_data['taskPlugin'] = self.plugin.get_task_plugin()
        plugin_data['xBased'] = self.plugin.get_x_based()
        plugin_data['createDate'] = self.plugin.get_create_date()
        plugin_data['modifyDate'] = self.plugin.get_modify_date()

        task_data = dict()
        task_data['id'] = self._id
        task_data['plugin'] = plugin_data
        task_data['commandClsId'] = self.command_cls_id
        task_data['parameterMap'] = self.parameter_map
        task_data['deleted'] = self.deleted
        task_data['cronExpression'] = self.cron_str
        task_data['createDate'] = self.create_date
        task_data['modifyDate'] = self.modify_date
        task_data['fileServerConf'] = self.file_server
        return task_data

    @property
    def obj_name(self):
        return "TASK"
