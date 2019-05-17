#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import json


class Plugin(object):
    """docstring for Plugin"""

    def __init__(self, message):
        self.plugin = message['plugin']

    @property
    def id(self):
        return self.plugin['id']

    @property
    def name(self):
        return self.plugin['name']

    @property
    def version(self):
        return self.plugin['version']

    @property
    def description(self):
        return self.plugin['description']

    def to_string(self):
        return str(self.plugin)

    def to_json(self):
        return json.load(self.plugin)
