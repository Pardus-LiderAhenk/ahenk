#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
from base.model.Plugin import Plugin
import json

class Task(object):
    """docstring for Task"""
    def __init__(self,message):
        self.task = message['task']

    @property
    def id(self):
        return self.task['id']

    @property
    def create_date(self):
        return self.task['createdate']

    @property
    def modify_date(self):
        return self.task['modifydate']

    @property
    def command_cls_id(self):
        return self.task['commandclsid']

    @property
    def parameter_map(self):
        return self.task['parametermap']

    @property
    def deleted(self):
        return self.task['deleted']

    @property
    def plugin(self):
        return Plugin(self.task['plugin'])

    def to_string(self):
        return str(self.task)

    def to_json(self):
        return json.load(self.task)




