#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json

class Task(object):
    """docstring for Task"""
    def __init__(self,message):
        self.payload = json.loads(message)
        self.request = self.payload['request']

    @property
    def task(self):
        self.request['task']

    @property
    def timestamp(self):
        self.request['timestamp']
