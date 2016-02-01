#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import imp,os
"""
 class AbstractPlugin(object):
     This is base class for plugins
     def __init__(self, arg):
         super(AbstrackPlugin, self).__init__()
         self.arg = arg
"""
pluginFolder = '/home/ismail/devzone/workspace/LiderAhenk/ahenk/opt/ahenk/plugins'
mainModule = 'main'

def getPlugins():
    plugins = []
    possibleplugins = os.listdir(pluginFolder)
    for i in possibleplugins:
        location = os.path.join(pluginFolder, i)
        if not os.path.isdir(location) or not mainModule + ".py" in os.listdir(location):
            continue
        info = imp.find_module(mainModule, [location])
        plugins.append({"name": i, "info": info})
    return plugins

def loadPlugin(plugin):
    return imp.load_module(mainModule, *plugin["info"])


if __name__ == '__main__':
    for i in getPlugins():
        print("Loading plugin " + i["name"])
        plugin = loadPlugin(i)
        plugin.run("tabisi")
