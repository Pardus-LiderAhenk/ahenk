#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import threading
from base.Scope import Scope

class Plugin(threading.Thread):
    """docstring for Plugin"""
    def __init__(self, name,InQueue):
        super(Plugin, self).__init__()
        self.name = name
        self.InQueue = InQueue
        self.scope=Scope.getInstance()
        self.pluginManager = self.scope.getPluginManager()

    def run():
        try:
            task=self.InQueue.get()
            command = self.pluginManager.findCommand(self.getName(),task.getCommandId())
            command.handle_task(task)
            # TODO add result to response queue

        except Exception as e:
            #TODO error log here
            print("exception occured when executing plugin")

    def getName(self):
        return self.name
