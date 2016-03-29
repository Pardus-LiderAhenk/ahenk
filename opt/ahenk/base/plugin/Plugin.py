#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import threading

from base.Scope import Scope


class Plugin(threading.Thread):
    """docstring for Plugin"""

    def __init__(self, name, InQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.InQueue = InQueue
        scope = Scope.getInstance()
        self.pluginManager = scope.getPluginManager()
        self.logger = scope.getLogger()

    def run(self):
        while True:
            try:
                item_obj = self.InQueue.get(block=True)
                obj_name = item_obj.obj_name
                print(obj_name)
                if obj_name == "TASK":
                    command = Scope.getInstance().getPluginManager().findCommand(self.getName(), item_obj.command_cls_id)
                    command.handle_task(item_obj)
                    # TODO add result to response queue
                elif obj_name == "PROFILE":
                    plugin = item_obj.plugin
                    plugin_name = plugin.name
                    profile_data = item_obj.profile_data
                    policy_module = Scope.getInstance().getPluginManager().findPolicyModule(plugin_name)
                    policy_module.handle_policy(profile_data)
                else:
                    self.logger.warning("Not supported object type " + obj_name)
            except Exception as e:
                # TODO error log here
                self.logger.error("Plugin running exception " + str(e))

    def getName(self):
        return self.name
