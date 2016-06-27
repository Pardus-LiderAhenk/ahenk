#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.Scope import Scope
from base.model.Task import Task


class ScheduleTaskDB(object):
    def __init__(self):
        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.db_service = scope.getDbService()

    def initialize(self):
        self.logger.debug('[ScheduleTaskDB] Initializing scheduler database...')
        self.db_service.check_and_create_table('schedule_task', ['id INTEGER PRIMARY KEY AUTOINCREMENT', 'task_id TEXT'])
        self.logger.debug('[ScheduleTaskDB] Scheduler database is ok.')

    def save(self, task):
        self.logger.debug('[ScheduleTaskDB] Preparing schedule task for save operation... creating columns and values...')
        cols = ['task_id']
        values = [task.get_id()]
        self.logger.debug('[ScheduleTaskDB] Saving scheduler task to db... ')
        self.db_service.update('schedule_task', cols, values, None)
        self.logger.debug('[ScheduleTaskDB] Scheduler task saved.')

    def delete(self, task_id):
        try:
            self.logger.debug('[ScheduleTaskDB] Deleting schedule task. Task id=' + str(task_id))
            self.db_service.delete('schedule_task', 'task_id=' + str(task_id))
            self.logger.debug('[ScheduleTaskDB] Deleting schedule task deleted successfully. task id=' + str(task_id))
        except Exception as e:
            self.logger.error('[ScheduleTaskDB] Exception occur when deleting schedule task ' + str(e))

    def load(self):
        try:
            self.logger.debug('[ScheduleTaskDB] Loading schedule tasks...')
            rows = self.db_service.select('schedule_task')
            tasks = []
            for row in rows:
                task_json = row['task_json']
                task = Task(None)
                task.from_json(task_json)
                tasks.append(task)
            self.logger.debug(
                '[ScheduleTaskDB] Schedule tasks loaded successfully. Schedule Tasks size=' + str(len(tasks)))
            return tasks
        except Exception as e:
            self.logger.error('[ScheduleTaskDB] Exception occur when loading schedule tasks! ' + str(e))
