#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import re

from base.plugin.abstract_plugin import AbstractPlugin


class DeleteDNS(AbstractPlugin):
    def __init__(self, task, context):
        super(DeleteDNS, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.dns_file = '/etc/resolv.conf'

        self.ip = self.task['ip']
        self.is_active = self.task['is_active']

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:

            lines = self.read_file_by_line(self.dns_file)
            f = open(self.dns_file, "w")

            for line in lines:
                line = str(line).strip(" ")
                # to remove multiple spaces
                line = re.sub(' +', ' ', line)

                if self.is_active is True:
                    if line != 'nameserver {}\n'.format(self.ip):
                        self.logger.debug(
                            'Writing a line to dns file... Line: {}'.format(line))
                        f.write(line)
                    else:
                        self.logger.debug('Line has been deleted from dns file. Line: {}'.format(line))
                else:
                    if line != '#nameserver {}\n'.format(self.ip) and line != '# nameserver {}\n'.format(self.ip):
                        self.logger.debug(
                            'Writing a line to dns file... Line: {}'.format(line))
                        f.write(line)
                    else:
                        self.logger.debug(
                            'Line has been deleted from dns file. Line: {}'.format(line))

            f.close()

            self.logger.info('NETWORK-MANAGER - DELETE_DNS task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='DNS bilgisi başarıyla silindi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    dns = DeleteDNS(task, context)
    dns.handle_task()
