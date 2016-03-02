#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import Queue

class PluginQueue(Queue.PriorityQueue):
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue
