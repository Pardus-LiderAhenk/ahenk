#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import time
from datetime import datetime, timedelta

from base.scheduler.base_scheduler import BaseScheduler
from base.scheduler.custom.schedule_job import ScheduleTaskJob
from base.scheduler.custom.scheduledb import ScheduleTaskDB
from base.scope import Scope


class CustomScheduler(BaseScheduler):
    def __init__(self):
        self.events = []
        self.keep_run = True
        self.logger = Scope.get_instance().get_logger()
        self.scheduledb = ScheduleTaskDB()

    def initialize(self):
        self.scheduledb.initialize()
        tasks = self.scheduledb.load()
        if tasks:
            for task in tasks:
                self.add_job(ScheduleTaskJob(task))

    def add_job(self, job):
        self.events.append(job)

    def save_and_add_job(self, task):
        try:
            self.logger.debug('Saving scheduled task to database...')
            self.scheduledb.save(task)
            self.logger.debug('Adding scheduled task to events...')
            self.events.append(ScheduleTaskJob(task))
        except Exception as e:
            self.logger.error(
                'A problem occurred while saving and adding job. Error Message: {0}'.format(str(e)))

    # unused
    def remove_job(self, task_id):
        for event in self.events:
            if event.task.get_id() == task_id:
                self.scheduledb.delete(task_id)
                self.logger.debug('Task was deleted from scheduled tasks table')
                self.events.remove(event)
                self.logger.debug('Task was removed from events')

    # unused
    def remove_job_via_task_id(self, task_id):
        for event in self.events:
            if event.task.get_id() == task_id:
                self.scheduledb.delete(event.task)
                self.events.remove(event)

    def stop(self):
        self.keep_run = False

    def list_schedule_tasks(self):
        return self.scheduledb.load()

    def run(self):
        t = datetime(*datetime.now().timetuple()[:5])

        while 1 and self.keep_run:
            if self.events is not None and len(self.events) > 0:

                for e in self.events:
                    e.check(t)

            t += timedelta(minutes=1)
            if datetime.now() < t:
                sl = (t - datetime.now()).seconds
                time.sleep(sl)
