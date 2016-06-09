#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class Sample(AbstractPlugin):
    def __init__(self, username, context):
        super(Sample, self).__init__()
        self.username = username
        self.context = context
        self.logger = self.get_logger()

    def handle_safe_mode(self):
        # TODO Do what do you want to do!
        pass


def handle_safe_mode(username, context):
    print('Sample Plugin Safe')
    sample = Sample(username, context)
    sample.handle_safe_mode()
