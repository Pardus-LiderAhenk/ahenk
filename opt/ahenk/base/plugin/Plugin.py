#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

class Plugin(object):
    """docstring for Plugin"""
    def __init__(self, name,mainModule):
        super(Plugin, self).__init__()
        self.name = name
        self.mainModule = mainModule

    def getName(self):
        return self.name

    def getMainModule(self):
        return self.mainModule
