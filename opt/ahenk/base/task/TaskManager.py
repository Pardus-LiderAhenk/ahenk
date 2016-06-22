#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.Scope import Scope
from base.model.MessageFactory import MessageFactory
from base.model.enum.MessageType import MessageType


class TaskManager(object):
    """docstring for TaskManager"""

    def __init__(self):
        # super(TaskManager, self).__init__()
        scope = Scope.getInstance()
        self.pluginManager = scope.getPluginManager()
        self.logger = scope.getLogger()
        self.db_service = scope.getDbService()
        self.scheduler = scope.get_scheduler()

    def addTask(self, task):
        try:
            self.saveTask(task)
            if task.get_cron_str() == None or task.get_cron_str() == '':
                self.logger.debug('[TaskManager] Adding task ... ')
                self.pluginManager.processTask(task)
            else:
                self.scheduler.save_and_add_job(task)

        except Exception as e:
            self.logger.debug('[TaskManager] Exception occured when adding task. Error Message: {}'.format(str(e)))

    def addPolicy(self, policy):
        try:
            self.pluginManager.processPolicy(policy)
        except Exception as e:
            self.logger.error("[TaskManager] Exception occured when adding policy. Error Message: {}".format(str(e)))
            pass

    def saveTask(self, task):
        try:
            task_cols = ['id', 'create_date', 'modify_date', 'command_cls_id', 'parameter_map', 'deleted', 'plugin','cron_expr']
            plu_cols = ['active', 'create_date', 'deleted', 'description', 'machine_oriented', 'modify_date', 'name', 'policy_plugin', 'user_oriented', 'version','task_plugin','x_based']
            plugin_args = [str(task.get_plugin().get_active()), str(task.get_plugin().get_create_date()), str(task.get_plugin().get_deleted()), str(task.get_plugin().get_description()), str(task.get_plugin().get_machine_oriented()), str(task.get_plugin().get_modify_date()), str(task.get_plugin().get_name()), str(task.get_plugin().get_policy_plugin()), str(task.get_plugin().get_user_oriented()), str(task.get_plugin().get_version()), str(task.get_plugin().get_task_plugin()), str(task.get_plugin().get_x_based())]
            plugin_id = self.db_service.update('plugin', plu_cols, plugin_args)
            values = [str(task.get_id()), str(task.get_create_date()), str(task.get_modify_date()), str(task.get_command_cls_id()), str(task.get_parameter_map()), str(task.get_deleted()), str(plugin_id),str(task.get_cron_str())]
            self.db_service.update('task', task_cols, values, None)
            # self.logger.debug('[TaskManager] Task has been saved to database (Task id:' + task.get_id() + ')')
        except Exception as e:
            print(str(e))

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
