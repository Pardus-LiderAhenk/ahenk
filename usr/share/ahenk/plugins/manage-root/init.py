#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class Init(AbstractPlugin):
    def __init__(self, context):
        super(Init, self).__init__()
        self.context = context
        self.logger = self.get_logger()

    def handle_mode(self):
        # TODO Do what do you want to do!
        pass


def handle_mode(context):
    init = Init(context)
    init.handle_mode()
