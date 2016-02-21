#!/usr/bin/python
# -*- coding: utf-8 -*-
# @author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>


class Scope(object):
    """docstring for Scope"""
    def __init__(self):
        super(Scope, self).__init__()
        self.customMap = {}
        self.configurationManager=None
        self.logger=None

    def getCustomMap(self):
        return self.customMap

    def putCustomMap(self,name,value):
        self.custom[str(name)]=value

    def getCustomParam(self,name):
        return self.customMap[str(name)]

    def getConfigurationManager(self):
        return self.configurationManager

    def setConfigurationManager(self,configurationManager):
        self.configurationManager = configurationManager

    def getLogger(self):
        return self.logger

    def setLogger(self,logger):
        self.logger = logger
