#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.scheduler.custom_scheduler_impl import CustomScheduler

class SchedulerFactory():

    def get_intstance(self):
        return CustomScheduler()