#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import threading

from base.scope import Scope


class TaskJob(threading.Thread):
    """docstring for TaskJob"""

    def __init__(self, task):
        super(TaskJob, self).__init__()
        scope = Scope.getInstance()
        self.task = task
        self.pluginManager = scope.getPluginManager()

    def run(self):
        self.pluginManager.process(self.task)
