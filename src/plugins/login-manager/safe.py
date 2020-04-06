#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.username = str(context.get_username())
        self.logger = self.get_logger()

        self.logger.debug('Parameters were initialized.')

    def handle_safe_mode(self):

        user_permission_file = '{0}login-manager/login_files/{1}.permissions'.format(self.Ahenk.plugins_path(),
                                                                                     self.username)
        if self.is_exist(user_permission_file):
            self.logger.debug('Delete permission file for user \'{0}\'...'.format(self.username))
            self.delete_file(user_permission_file)

        machine_permission_file = '{0}login-manager/login_files/None.permissions'.format(self.Ahenk.plugins_path())
        if self.is_exist(machine_permission_file):
            self.logger.debug('Delete permission file for machine...')
            self.delete_file(machine_permission_file)


def handle_mode(context):
    safe = Safe(context)
    safe.handle_safe_mode()
