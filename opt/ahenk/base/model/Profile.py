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
    def params(self):
        return self.profile['params']

    @property
    def date(self):
        return self.profile['date']

    @property
    def plugin(self):
        return Plugin(self.profile['plugin'])
