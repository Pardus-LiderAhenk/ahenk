#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class Login(AbstractPlugin):
    def __init__(self, context):
        super(Login, self).__init__()
        self.context = context
        self.username = str(context.get_username())
        self.logger = self.get_logger()

    def handle_mode(self):
        # TODO Do what do you want to do!
        pass


def handle_mode(context):
    login = Login(context)
    login.handle_mode()
