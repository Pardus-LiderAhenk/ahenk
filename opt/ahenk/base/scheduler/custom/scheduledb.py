#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.model.task import Task
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
            tasks = []
            for row in rows:
                task_json = row['task_json']
                task = Task(None)
                task.from_json(task_json)
                tasks.append(task)
            self.logger.debug(
                'Schedule tasks loaded successfully. Schedule Tasks size=' + str(len(tasks)))
            return tasks
        except Exception as e:
            self.logger.error('Exception occur when loading schedule tasks! ' + str(e))
