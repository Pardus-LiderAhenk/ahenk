#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.Scope import Scope


class AbstractCommand(object):
    """docstring for AbstractCommand"""

    def __init__(self):
        super(AbstractCommand, self).__init__()
        self.scope = Scope.getInstance()

    def handle_task(task):
        # implement this metot from command
        pass

    def logger(self):
        try:
            return self.scope.getLogger()
        except Exception as e:
            print('Logger did not found')
            return None

    def configurationManager(self):
        try:
            return self.scope.getConfigurationManager()
        except Exception as e:
            print('ConfigurationManager did not found')
            return None

    def addMessageResponseQueue(self):
        # TODO implement response queue
        pass
