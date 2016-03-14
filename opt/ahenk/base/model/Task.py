#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json

class Task(object):
    """docstring for Task"""
    def __init__(self,message):
        self.payload = json.loads(message)
        self.request = self.payload[u'request']

    @property
    def task_id(self):
        self.request[u'id']

    @property
    def plugin_name(self):
        self.request[u'pluginName']

    @property
    def command_id(self):
        self.request[u'commandId']

    @property
    def params(self):
        self.request[u'parameterMap']

    @property
    def plugin_version(self):
        self.request[u'pluginVersion']
