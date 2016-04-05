#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.scheduler.custom.all_match import AllMatch
from base.Scope import Scope

class ScheduleTaskJob(object):
    def __init__(self, task):
        self.task = task
        cron_sj = self.parse_cron_str(task.cron_str)
        if cron_sj:
            self.mins = self.conv_to_set(cron_sj[0])
            self.hours= self.conv_to_set(cron_sj[1])
            self.days = self.conv_to_set(cron_sj[2])
            self.months = self.conv_to_set(cron_sj[3])
            self.dow = self.conv_to_set(cron_sj[4])
            self.action = self.processTask
        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.task_manager = scope.getTaskManager()

    def processTask(self):
        try:
            self.task_manager.addTask(self.task)
        except Exception as e:
            self.logger.error(e)

    def parse_cron_str(self,cron_str):
        try:
            cron_exp_arr = cron_str.split(" ")
            cron_sj = []
            count = 0
            for exp in cron_exp_arr:
                if exp.isdigit():
                    cron_sj.append(exp)
                elif '*' == exp:
                    cron_sj.append(AllMatch())
                elif '/' in exp:
                    range_val = int(exp.split("/")[1])
                    if count == 0:
                        cron_sj.append(range(0, 60, range_val))
                    elif count == 1:
                        cron_sj.append(range(0, 24, range_val))
                    elif count == 2:
                        cron_sj.append(range(0, 7, range_val))
                    elif count == 3:
                        cron_sj.append(range(0, 12, range_val))
                    elif count == 3:
                        cron_sj.append(range(0, 7, range_val))
                    else:
                        print("it is not supported")
                elif ',' in exp:
                    cron_sj.append("(" + str(exp) + ")")
                else:
                    print("it is not supported")
                count = count + 1
            return cron_sj
        except Exception as e:
            self.logger.error(str(e))

    def conv_to_set(obj):
        if isinstance(obj, (int)):
            return set([obj])
        if not isinstance(obj, set):
            obj = set(obj)
        return obj


    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute     in self.mins) and
                (t.hour       in self.hours) and
                (t.day        in self.days) and
                (t.month      in self.months) and
                (t.weekday()  in self.dow))

    def check(self, t):
        if self.matchtime(t):
            self.action(*self.args, **self.kwargs)