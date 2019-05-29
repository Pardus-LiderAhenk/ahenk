#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>


class PluginBean(object):
    """docstring for PluginBean"""

    def __init__(self, p_id=None, active=None, create_date=None, deleted=None, description=None, machine_oriented=None, modify_date=None, name=None, policy_plugin=None, task_plugin=None, user_oriented=None, version=None, x_based=None):
        self.id = p_id
        self.active = active
        self.create_date = create_date
        self.deleted = deleted
        self.description = description
        self.machine_oriented = machine_oriented
        self.modify_date = modify_date
        self.name = name
        self.policy_plugin = policy_plugin
        self.user_oriented = user_oriented
        self.version = version
        self.task_plugin = task_plugin
        self.x_based = x_based

    def get_user_oriented(self):
        return self.user_oriented

    def set_user_oriented(self, user_oriented):
        self.user_oriented = user_oriented

    def get_policy_plugin(self):
        return self.policy_plugin

    def set_policy_plugin(self, policy_plugin):
        self.policy_plugin = policy_plugin

    def get_machine_oriented(self):
        return self.machine_oriented

    def set_machine_oriented(self, machine_oriented):
        self.machine_oriented = machine_oriented

    def get_modify_date(self):
        return self.modify_date

    def set_modify_date(self, modify_date):
        self.modify_date = modify_date

    def get_create_date(self):
        return self.create_date

    def set_create_date(self, create_date):
        self.create_date = create_date

    def get_deleted(self):
        return self.deleted

    def set_deleted(self, deleted):
        self.deleted = deleted

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_active(self):
        return self.active

    def set_active(self, active):
        self.active = active

    def get_id(self):
        return self.id

    def set_id(self, p_id):
        self.id = p_id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version

    def get_x_based(self):
        return self.x_based

    def set_x_based(self, x_based):
        self.x_based = x_based

    def get_task_plugin(self):
        return self.task_plugin

    def set_task_plugin(self, task_plugin):
        self.task_plugin = task_plugin
