#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import re

from base.plugin.abstract_plugin import AbstractPlugin


class DeleteHost(AbstractPlugin):
    def __init__(self, task, context):
        super(DeleteHost, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.hosts_file = '/etc/hosts'

        self.ip = self.task['ip']
        self.hostname = self.task['hostname']
        self.is_active = self.task['is_active']

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:

            lines = self.read_file_by_line(self.hosts_file)
            f = open(self.hosts_file, "w")

            for line in lines:
                line = str(line).strip(" ")
                # to remove multiple spaces
                line = re.sub(' +', ' ', line)

                if self.is_active is True:
                    if line != '{0} {1}\n'.format(self.ip, self.hostname):
                        self.logger.debug(
                            'Writing a line to hosts file... Line: {}'.format(line))
                        f.write(line)
                    else:
                        self.logger.debug(
                            'Line has been deleted from hosts file. Line: {}'.format(line))
                else:
                    if line != '#{0} {1}\n'.format(self.ip, self.hostname) and line != '# {0} {1}\n'.format(self.ip,
                                                                                                            self.hostname):
                        self.logger.debug(
                            'Writing a line to hosts file... Line: {}'.format(line))
                        f.write(line)
                    else:
                        self.logger.debug(
                            'Line has been deleted from hosts file. Line: {}'.format(line))

            f.close()

            self.logger.info('NETWORK-MANAGER - DELETE_HOST task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Sunucu bilgisi başarıyla silindi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    host = DeleteHost(task, context)
    host.handle_task()
