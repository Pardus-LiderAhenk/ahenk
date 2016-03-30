#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime

class Result(object):
    """docstring for Plugin"""

    def __init__(self, type, id, code=None, message=None, context=None):
        self.type = type
        self.id = id
        self.code = code
        self.message = message
        self.context = context.data
        self.content_type = context.content_type
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
        return self.id

    def set_message(self, message):
        self.message = message

    def get_data(self):
        return self.context.data

    def set_data(self, data):
        self.context.data = data

    def get_content_type(self):
        return self.context.content_type

    def set_content_type(self, content_type):
        self.context.content_type = content_type

    def get_timestamp(self):
        return self.timestamp

class Context():
    def __init__(self, data=None, content_type=None):
        self.data = type
        self.content_type = id
