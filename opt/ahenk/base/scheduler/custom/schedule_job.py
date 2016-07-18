#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.scheduler.custom.all_match import AllMatch
from base.Scope import Scope


# TODO Need logs
class ScheduleTaskJob(object):
    def __init__(self, task):
        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.task_manager = scope.getTaskManager()
        self.plugin_manager = scope.getPluginManager()
        self.task = task
        cron_sj = self.parse_cron_str(task.get_cron_str())
        try:
            if cron_sj:
                self.mins = self.conv_to_set(cron_sj[0])
                self.hours = self.conv_to_set(cron_sj[1])
                self.days = self.conv_to_set(cron_sj[2])
                self.months = self.conv_to_set(cron_sj[3])
                self.dow = self.conv_to_set(cron_sj[4])
                self.action = self.process_task
            self.logger.debug('[ScheduleTaskJob] Instance created.')
        except Exception as e:
            self.logger.error('[ScheduleTaskJob] A problem occurred while creating instance of ScheduleTaskJob. Error Message : {}'.format(str(e)))

    def process_task(self):
        try:
            self.logger.debug('[ScheduleTaskJob] Running scheduled task now...')
            self.plugin_manager.process_task(self.task)
            self.logger.debug('[ScheduleTaskJob] Scheduled Task was executed.')
            if self.is_single_shot():
                Scope.getInstance().get_scheduler().remove_job(self.task.get_id())
        except Exception as e:
            self.logger.error('[ScheduleTaskJob] A problem occurred while running scheduled task. Error Message: {}'.format(str(e)))

    def parse_cron_str(self, cron_str):
        self.logger.debug('[ScheduleTaskJob] Parsing cron string...')
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
                        self.logger.warning('[ScheduleTaskJob] Unsupported expression.')
                elif ',' in exp:
                    cron_sj.append("(" + str(exp) + ")")
                else:
                    self.logger.warning('[ScheduleTaskJob] Unsupported expression.')
                count = count + 1
            return cron_sj
        except Exception as e:
            self.logger.error('[ScheduleTaskJob] A problem occurred while parsing cron expression. Error Message: {}'.format(str(e)))

    def conv_to_set(self, obj):
        self.logger.debug('[ScheduleTaskJob] Converting {} to set'.format(str(obj)))

        if str(obj).isdigit():
            return set([int(obj)])
        if not isinstance(obj, set):
            obj = set(obj)

        return obj

    def is_single_shot(self):
        if '*' in self.task.cron_str:
            return True
        else:
            return False

    def matchtime(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute in self.mins) and
                (t.hour in self.hours) and
                (t.day in self.days) and
                (t.month in self.months) and
                (t.weekday() in self.dow))

    def check(self, t):
        if self.matchtime(t) is True:
            self.action()
