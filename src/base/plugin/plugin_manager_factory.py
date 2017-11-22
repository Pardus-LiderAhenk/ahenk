#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.plugin.plugin_manager import PluginManager


class PluginManagerFactory(object):
    def get_instance():
        return PluginManager()

    get_instance = staticmethod(get_instance)
