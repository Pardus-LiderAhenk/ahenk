#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
from base.model.Plugin import Plugin
import json

class Profile(object):
    """docstring for Profile"""
    def __init__(self,message):
        self.profile = message

    @property
    def id(self):
        return self.profile['id']

    @property
    def create_date(self):
        return self.profile['createdate']

    @property
    def modify_date(self):
        return self.profile['modifydate']

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
