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
    def label(self):
        return self.profile['label']

    @property
    def description(self):
        return self.profile['description']

    @property
    def is_overridable(self):
        return self.profile['isoverridable']

    @property
    def is_active(self):
        return self.profile['isactive']

    @property
    def modify_date(self):
        return self.profile['modifydate']

    @property
    def profile_data(self):
        return self.profile['profiledata']

    @property
    def plugin(self):
        return Plugin(self.profile['plugin'])
