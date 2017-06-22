#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Caner Feyzullahoglu <caner.feyzullahoglu@agem.com.tr>
"""
Style Guide is PEP-8
https://www.python.org/dev/peps/pep-0008/
"""

import json
import os
from base.plugin.abstract_plugin import AbstractPlugin


class UserPrivilegeSafeMode(AbstractPlugin):
    def __init__(self, context):
        super(AbstractPlugin, self).__init__()
        self.username = str(context.get_username())
        self.context = context
        self.logger = self.get_logger()

    def handle_safe_mode(self):
        self.logger.debug('Handling safe mode.')

        self.logger.debug('Getting plugin path.')
        p_path = self.Ahenk.plugins_path()
        privilege_file = p_path + 'user-privilege/privilege.changes/' + self.username + '.changes'

        if self.is_exist(privilege_file):
            self.logger.debug('Reading privilege_file: ' + privilege_file)
            with open(privilege_file) as data_file:
                self.logger.debug('Creating object from JSON data file.')
                data = json.load(data_file)

            command_path_list = data['command_path_list']
            added_user_list = data['added_user_list']
            deleted_user_list = data['deleted_user_list']

            if len(command_path_list) != 0:
                self.logger.debug('Removing wrapper files and renaming original files.')

                for command_path in command_path_list:
                    if os.path.exists(command_path + '-ahenk'):
                        self.logger.debug('Executing: ' + '"rm ' + command_path + '"')
                        self.execute('rm ' + command_path)
                        self.logger.debug(
                            'Executing: ' + '"mv ' + command_path + '-ahenk ' + command_path + '"')
                        self.execute('mv ' + command_path + '-ahenk ' + command_path)
                    else:
                        self.logger.debug(
                            'File will not be deleted because ' + command_path + 'does not exists.')

            if len(added_user_list) != 0:
                self.logger.debug('Removing user from groups that it has been added in advance.')

                for group_name in added_user_list:
                    self.logger.debug(
                        'Executing: ' + '"deluser ' + str(self.username) + ' ' + group_name + '"')
                    self.execute('deluser ' + str(self.username) + ' ' + group_name)

            if len(deleted_user_list) != 0:
                self.logger.debug('Adding user to groups that it has been removed in advance.')

                for group_name in deleted_user_list:
                    self.logger.debug(
                        'Executing: ' + '"adduser ' + str(self.username) + ' ' + group_name + '"')
                    self.execute('adduser ' + str(self.username) + ' ' + group_name)
        else:
            self.logger.debug('Changes file not found for {} user.'.format(self.username))


def handle_mode(context):
    user_privilege = UserPrivilegeSafeMode(context)
    user_privilege.handle_safe_mode()
