#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.Scope import Scope
from base.model.MessageFactory import MessageFactory
from base.model.MessageType import MessageType


class TaskManager(object):
    """docstring for TaskManager"""

    def __init__(self):
        # super(TaskManager, self).__init__()
        scope = Scope.getInstance()
        self.pluginManager = scope.getPluginManager()
        self.logger = scope.getLogger()
        self.db_service = scope.getDbService()

    def addTask(self, task):
        try:
            self.logger.debug('Adding task ... ')
            # self.saveTask(task)
            self.logger.info('Task saved ')
            # TODO send task received message
            self.pluginManager.processTask(task)
        except Exception as e:
            # TODO error log here
            self.logger.debug('Exception occured when adding task ' + str(e))
            pass

    def saveTask(self, task):
        cols = ['id', 'create_date', 'modify_date', 'command_cls_id', 'parameter_map', 'deleted', 'plugin']
        values = [str(task.id), str(task.create_date), str(task.modify_date), str(task.command_cls_id), str(task.parameter_map), str(task.deleted), task.plugin.to_string()]
        self.db_service.update('task', cols, values, None)
        self.logger.debug('[TaskManager] Task has been saved to database (Task id:' + task.id + ')')

    def updateTask(self, task):
        # TODO not implemented yet
        # This is updates task status processing - processed ...
        pass

    def deleteTask(self, task):
        # TODO not implemented yet
        # remove task if it is processed
        pass

    def sendMessage(self, type, message):
        # TODO not implemented yet
        pass


if __name__ == '__main__':
    print(MessageFactory.createMessage(MessageType.TASK_PROCESSING, "my message"))
