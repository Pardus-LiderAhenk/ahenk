#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.model.task_bean import TaskBean
from base.model.plugin_bean import PluginBean
from base.scope import Scope


class ScheduleTaskDB(object):
    def __init__(self):
        scope = Scope.get_instance()
        self.logger = scope.get_logger()
        self.db_service = scope.get_db_service()

    def initialize(self):
        self.logger.debug('Initializing scheduler database...')
        self.db_service.check_and_create_table('schedule_task',
                                               ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'task_id TEXT'])
        self.logger.debug('Scheduler database is ok.')

    def save(self, task):
        self.logger.debug('Preparing schedule task for save operation... creating columns and values...')
        cols = ['task_id']
        values = [task.get_id()]
        self.logger.debug('Saving scheduler task to db... ')
        self.db_service.update('schedule_task', cols, values, None)
        self.logger.debug('Scheduler task saved.')

    def delete(self, task_id):
        try:
            self.logger.debug('Deleting schedule task. Task id=' + str(task_id))
            self.db_service.delete('schedule_task', 'task_id=' + str(task_id))
            self.logger.debug('Deleting schedule task deleted successfully. task id=' + str(task_id))
        except Exception as e:
            self.logger.error('Exception occur when deleting schedule task ' + str(e))

    def load(self):
        try:
            self.logger.debug('Loading schedule tasks...')
            rows = self.db_service.select('schedule_task')
            tasks = list()
            for row in rows:
                tasks.append(self.get_task_by_id(row[1]))
            self.logger.debug(
                'Scheduled tasks are loaded successfully. Scheduled Tasks size is {0}'.format(str(len(tasks))))
            return tasks
        except Exception as e:
            self.logger.error(
                'Exception occurred while loading schedule tasks. Error Message: {0}'.format(str(e)))

    def get_task_by_id(self, task_id):
        self.logger.debug('Getting task from db.')
        try:
            db_task = self.db_service.select('task', criteria='id={0}'.format(task_id))[0]
            return TaskBean(db_task[0], db_task[1], db_task[2], db_task[3], db_task[4], db_task[5],
                            self.get_plugin_by_id(db_task[6]), db_task[7], db_task[8])
        except Exception as e:
            self.logger.debug('A problem occurred while getting task by id. Error Message: {0}'.format(str(e)))

    def get_plugin_by_id(self, plugin_id):
        self.logger.debug('Getting plugin from db.')
        db_plugin = self.db_service.select('plugin', criteria='id={0}'.format(plugin_id))[0]
        return PluginBean(db_plugin[0], db_plugin[1], db_plugin[2], db_plugin[3], db_plugin[4], db_plugin[5],
                          db_plugin[6], db_plugin[7], db_plugin[8], db_plugin[11], db_plugin[9], db_plugin[10],
                          db_plugin[12])

