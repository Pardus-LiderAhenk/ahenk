#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json

class Task(object):
    """docstring for Task"""
    def __init__(self,message):
        self.payload = json.loads(message)
        print(self.payload)
        self.request = self.payload['request']
        print(self.request)

    @property
    def task_id(self):
        self.request['id']

    @property
    def plugin_name(self):
        self.request['pluginName']

    @property
    def command_id(self):
        self.request['commandId']

    @property
    def params(self):
        self.request['parameterMap']

    @property
    def plugin_version(self):
        self.request['pluginVersion']
