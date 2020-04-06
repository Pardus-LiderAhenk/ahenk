#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class Sample(AbstractPlugin):
    def __init__(self, task, context):
        super(Sample, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()

    def handle_task(self):
        # TODO Do what do you want to do!
        # TODO Don't Forget returning response with <self.context.create_response(..)>
        pass


def handle_task(task, context):
    print('Sample Plugin Task')
    sample = Sample(task, context)
    sample.handle_task()
