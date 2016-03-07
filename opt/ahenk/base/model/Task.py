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
    def getPluginName(self):
        self.request[u'pluginName']

    @property
    def getCommandId(self):
        self.request[u'commandId']

    @property
    def params(self):
        self.request[u'parameterMap']

    @property
    def pluginVersion(self):
        self.request[u'pluginVersion']
