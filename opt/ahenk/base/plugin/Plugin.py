#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import threading
from base.Scope import Scope

class Plugin(threading.Thread):
    """docstring for Plugin"""
    def __init__(self, name,InQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.InQueue = InQueue
        scope = Scope.getInstance()
        self.pluginManager = scope.getPluginManager()
        self.logger = scope.getLogger()

    def run(self):
        while True :
            try:
                task=self.InQueue.get(block=True)
                command = Scope.getInstance().getPluginManager().findCommand(self.getName(),task.command_cls_id)
                command.handle_task(task)
                # TODO add result to response queue

            except Exception as e:
                #TODO error log here
                self.logger.error("Plugin running exception " + str(e))

    def getName(self):
        return self.name
