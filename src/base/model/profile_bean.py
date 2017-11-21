#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import json

from base.model.plugin_bean import PluginBean


class ProfileBean(object):
    """docstring for Profile"""

    def __init__(self, p_id=None, create_date=None, label=None, description=None, overridable=None, active=None, deleted=None, profile_data=None, modify_date=None, plugin=None, username=None):
        self.id = p_id
        self.create_date = create_date
        self.modify_date = modify_date
        self.label = label
        self.description = description
        self.overridable = overridable
        self.active = active
        self.deleted = deleted
        self.profile_data = profile_data
        self.plugin = plugin
        self.username = username

    def get_id(self):
        return self.id

    def set_id(self, p_id):
        self.id = p_id

    def get_create_date(self):
        return self.create_date

    def set_create_date(self, create_date):
        self.create_date = create_date

    def get_modify_date(self):
        return self.modify_date

    def set_modify_date(self, modify_date):
        self.modify_date = modify_date

    def get_label(self):
        return self.label

    def set_label(self, label):
        self.label = label

    def get_description(self):
        return self.modify_date

    def set_description(self, description):
        self.description = description

    def get_overridable(self):
        return self.overridable

    def set_overridable(self, overridable):
        self.overridable = overridable

    def get_active(self):
        return self.active

    def set_active(self, active):
        self.active = active

    def get_deleted(self):
        return self.deleted

    def set_deleted(self, deleted):
        self.deleted = deleted

    def get_profile_data(self):
        return self.profile_data

    def set_profile_data(self, profile_data):
        self.profile_data = profile_data

    def get_plugin(self):
        return self.plugin

    def set_plugin(self, plugin):
        self.plugin = plugin

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    @property
    def obj_name(self):
        return "PROFILE"