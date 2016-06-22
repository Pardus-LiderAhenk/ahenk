#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.scheduler.custom.custom_scheduler import CustomScheduler

class SchedulerFactory():

    def get_intstance():
        return CustomScheduler()

    get_intstance = staticmethod(get_intstance)