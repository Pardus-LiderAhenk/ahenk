#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.scheduler.APSchedulerImpl import APSchedulerImpl

class SchedulerFactory():

    def get_intstance(self):
        return APSchedulerImpl()