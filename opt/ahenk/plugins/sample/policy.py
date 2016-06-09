#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class Sample(AbstractPlugin):
    def __init__(self, profile_data, context):
        super(Sample, self).__init__()
        self.profile_data = profile_data
        self.context = context
        self.logger = self.get_logger()

    def handle_policy(self):
        # TODO Do what do you want to do!
        # TODO Don't Forget returning response with <self.context.create_response(..)>
        pass


def handle_policy(profile_data, context):
    print('Sample Plugin Policy')
    sample = Sample(profile_data, context)
    sample.handle_policy()
