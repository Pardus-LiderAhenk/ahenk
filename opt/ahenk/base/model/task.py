#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import json

from base.model.plugin import Plugin


class Task(object):
    """docstring for Task"""

    def __init__(self, message):
        #TODO message must be json !!! otherwise we can not use task json methods!
        #Remove if condition and change message param to json task type.
        if message:
            self.task = message['task']

    @property
    def id(self):
        return self.task['id']

    @property
    def create_date(self):
        return self.task['createDate']

    @property
    def modify_date(self):
        return self.task['modifyDate']

    @property
    def command_cls_id(self):
        return json.loads(str(self.task))['commandClsId']

    @property
    def parameter_map(self):
        return self.task['parameterMap']

    @property
    def deleted(self):
        return self.task['deleted']

    @property
    def plugin(self):
        return Plugin(json.loads(str(self.task)))

    @property
    def cron_str(self):
        return '1 * * * *'   #TODO update when task cron field added.

    def to_string(self):
        return str(self.task)

    def to_json(self):
        return json.dumps(self.task)

    def from_json(self,json_value):
        self.task = json.load(json_value)

    @property
    def obj_name(self):
        return "TASK"

    def cols(self):
        return ['id', 'create_date', 'modify_date', 'command_cls_id', 'parameter_map', 'deleted', 'plugin']

    def values(self):
        return [str(self.id), str(self.create_date), str(self.modify_date), str(self.command_cls_id), str(self.parameter_map), str(self.deleted), self.plugin.to_string()]
