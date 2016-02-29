#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>


 class AbstractPlugin(object):
     """This is base class for plugins"""
     def __init__(self, arg):
         super(AbstrackPlugin, self).__init__()
         self.arg = arg
