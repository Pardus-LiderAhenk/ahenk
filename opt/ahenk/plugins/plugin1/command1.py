#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.plugin.AbstractCommand import AbstractCommand

class MySamplePlugin(AbstractCommand):
    """docstring for MySamplePlugin"""
    def __init__(self, task):
        super(MySamplePlugin, self).__init__()
        self.task = task

    def handle_task(self):
        print("This is command 1 ")


def handle_task(task):
    # Do what ever you want here
    # You can create command class but it is not necessary
    # You can use directly this method.
    myPlugin = MySamplePlugin(task)
    myPlugin.handle_task()
