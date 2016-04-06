#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.scheduler.base_scheduler import BaseScheduler
from base.Scope import Scope
from base.scheduler.custom.scheduledb import ScheduleTaskDB
from base.scheduler.custom.schedule_job import ScheduleTaskJob
from datetime import datetime, timedelta
import time


class CustomScheduler(BaseScheduler):

    def __init__(self):
        self.events = []
        self.keep_run = True
        self.logger = Scope.getInstance().getLogger()
        self.scheduledb = ScheduleTaskDB()

    def initialize(self):
        self.scheduledb.initialize()
        tasks = self.scheduledb.load()
        for task in tasks:
            self.add_job(ScheduleTaskJob(task))

    def add_job(self, job):
        self.events.append(job)

    def save_and_add_job(self, task):
        self.scheduledb.save(task)
        self.events.append(ScheduleTaskJob(task))

    def remove_job(self, task):
        for event in self.events:
            if event.task.id == task.id:
                self.scheduledb.delete(task)
                self.events.remove(event)

    def remove_job_via_task_id(self,task_id):
        for event in self.events:
            if event.task.id == task_id:
                self.scheduledb.delete(event.task)
                self.events.remove(event)

    def stop(self):
        self.keep_run = False

    def list_schedule_tasks(self):
        return self.scheduledb.load()

    def run(self):
        t = datetime(*datetime.now().timetuple()[:5])
        while 1 and self.keep_run:
            for e in self.events:
                e.check(t)

            t += timedelta(minutes=1)
            while datetime.now() < t:
                time.sleep((t - datetime.now()).seconds)




