#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import json

from base.model.plugin import Plugin


class Profile(object):
    """docstring for Profile"""

    def __init__(self, message):
        self.profile = message
        self.username = None

    @property
    def id(self):
        return self.profile['id']

    @property
    def create_date(self):
        return self.profile['createDate']

    @property
    def modify_date(self):
        return self.profile['modifyDate']

    @property
    def label(self):
        return self.profile['label']

    @property
    def description(self):
        return self.profile['description']

    @property
    def overridable(self):
        return self.profile['overridable']

    @property
    def active(self):
        return self.profile['active']

    @property
    def deleted(self):
        return self.profile['deleted']

    @property
    def profile_data(self):
        return self.profile['profileData']

    @property
    def plugin(self):
        return Plugin(self.profile['plugin'])

    def to_string(self):
        return str(self.profile)

    def to_json(self):
        return json.load(self.profile)

    @property
    def obj_name(self):
        return "PROFILE"

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username
