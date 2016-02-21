#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>


class Scope(object):
    """docstring for Scope"""
    def __init__(self):
        super(Scope, self).__init__()
        self.customMap = {}
        self.configurationManager=None

    def getCustomMap(self):
        return self.customMap

    def putCustomMap(self,name,value):
        self.custom[name]=value

    def getConfigurationManager(self):
        return self.configurationManager

    def serConfigurationManager(self,configurationManager):
        self.configurationManager = configurationManager
