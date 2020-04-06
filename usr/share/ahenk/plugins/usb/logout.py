#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Logout(AbstractPlugin):
    def __init__(self, context):
        super(Logout, self).__init__()
        self.context = context
        self.logger = self.get_logger()

        self.logger.debug('Parameters were initialized.')

    def handle_logout_mode(self):
        if self.is_exist("/etc/udev/rules.d/99-whitelist.rules"):
            self.delete_file("/etc/udev/rules.d/99-whitelist.rules")
        if self.is_exist("/etc/udev/rules.d/99-blacklist.rules"):
            self.delete_file("/etc/udev/rules.d/99-blacklist.rules")


def handle_mode(context):
    logout = Logout(context)
    logout.handle_logout_mode()