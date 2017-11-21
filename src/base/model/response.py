#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime


class Response(object):
    """docstring for Plugin"""

    def __init__(self, type, id, code=None, message=None, data=None, content_type=None, execution_id=None, policy_version=None):
        self.type = type
        self.id = id
        self.code = code
        self.message = message
        self.data = data
        self.content_type = content_type
        self.execution_id = execution_id
        self.policy_version = policy_version
        self.timestamp = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))

    def get_type(self):
        return str(self.type)

    def set_type(self, type):
        self.type = type

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_code(self):
        return str(self.code)

    def set_code(self, code):
        self.code = code

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_content_type(self):
        return self.content_type

    def set_content_type(self, content_type):
        self.content_type = content_type

    def get_timestamp(self):
        return self.timestamp

    def get_execution_id(self):
        return str(self.execution_id)

    def set_execution_id(self, execution_id):
        self.execution_id = execution_id

    def get_policy_version(self):
        return self.policy_version

    def set_policy_version(self, policy_version):
        self.policy_version = policy_version
