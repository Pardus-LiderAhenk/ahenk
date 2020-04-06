#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Mine Dogan <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class GrantSudoAccess(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.sudoer_line = '{0} ALL = NOPASSWD : /usr/bin/apt-get, /usr/bin/apt , /usr/bin/aptitude'
        self.sudoer_file_path = '/etc/sudoers.d/{0}_sudoers'
        self.logger = self.get_logger()

    def handle_policy(self):

        username = self.context.get('username')

        try:
            if username is not None:
                json_data = json.loads(self.data)

                if str(json_data['privilege']) == 'True':
                    if self.is_exist(self.sudoer_file_path):
                        self.logger.debug('User sudoers is exist privilege to {}'.format(username))
                    else:
                        self.create_file(self.sudoer_file_path.format(username))

                        sudoer_data = self.read_file(self.sudoer_file_path.format(username))
                        self.write_file(self.sudoer_file_path.format(username), sudoer_data.replace(self.sudoer_line.format(username),
                                                                               '') + '\n' + self.sudoer_line.format(username) + '\n')

                        self.logger.debug('User sudoers set privilege to {0}.'.format(username))

                        self.logger.debug('Creating response...')
                        self.context.create_response(self.get_message_code().POLICY_PROCESSED.value,
                                                 'User sudoers set privilege to {} successfully.'.format(username))

                elif str(json_data['privilege']) == 'False':

                    if self.is_exist(self.sudoer_file_path.format(username)):
                        self.delete_file(self.sudoer_file_path.format(username))
                        self.logger.debug('User sudoers removed privilege from {0}.'.format(username))
                        self.logger.debug('Creating response...')
                        self.context.create_response(self.get_message_code().POLICY_PROCESSED.value,
                                                     'User sudoers removed privilege from {0} successfully.'.format(username))
                    else:
                        self.logger.debug("{0} user's privilege file not found".format(username))

                else:
                    self.context.create_response(self.get_message_code().POLICY_PROCESSED.value, 'Missing parameter error.')

                self.logger.debug('Sudoers profile is handled successfully.')
            else:
                self.logger.error('Username parameter is missing.')
                self.context.create_response(self.get_message_code().POLICY_ERROR.value, 'Username is missing')

        except Exception as e:
            self.logger.error('A problem occurred while handling sudoers profile: {0}'.format(str(e)))
            self.context.create_response(self.get_message_code().POLICY_ERROR.value,
                                         'A problem occurred while handling sudoers profile: {0}'.format(str(e)))


def handle_policy(profile_data, context):
    quota = GrantSudoAccess(profile_data, context)
    quota.handle_policy()
