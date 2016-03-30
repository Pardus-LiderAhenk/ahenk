#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import threading

from base.Scope import Scope

class Context(object):
    def __init__(self):
        self.data = {}

    def put(self,var_name,data):
        self.data[var_name] = data

    def empty_data(self):
        self.data = {}

class Plugin(threading.Thread):
    """
        This is a thread inherit class and have a queue.
        Plugin class responsible for processing TASK or USER PLUGIN PROFILE.
    """

    def __init__(self, name, InQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.InQueue = InQueue
        scope = Scope.getInstance()
        self.logger = scope.getLogger()
        self.keep_run = True
        self.context = Context()

    def run(self):
        while self.keep_run:
            try:
                item_obj = self.InQueue.get(block=True)
                obj_name = item_obj.obj_name
                print(obj_name)
                if obj_name == "TASK":
                    command = Scope.getInstance().getPluginManager().findCommand(self.getName(), item_obj.command_cls_id)
                    command.handle_task(item_obj,self.context)
                    # TODO create response message from context and item_obj. item_obj is task


                    # Empty context for next use
                    self.context.empty_data()

                    # TODO add result to response queue
                elif obj_name == "PROFILE":
                    plugin = item_obj.plugin
                    plugin_name = plugin.name
                    profile_data = item_obj.profile_data
                    policy_module = Scope.getInstance().getPluginManager().findPolicyModule(plugin_name)

                    policy_module.handle_policy(profile_data,self.context)
                    # TODO create response message from context and item_obj. item_obj is profile

                    # Empty context for next use
                    self.context.empty_data()

                elif obj_name == "KILL_SIGNAL":
                    self.keep_run = False
                    self.logger.debug('[Plugin] Killing queue ! Plugin Name : ' + str(self.name))
                else:
                    self.logger.warning("[Plugin] Not supported object type " + obj_name)
            except Exception as e:
                # TODO error log here
                self.logger.error("[Plugin] Plugin running exception " + str(e))

    def getName(self):
        return self.name
