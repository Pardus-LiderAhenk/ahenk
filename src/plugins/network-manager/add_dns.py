#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class AddDNS(AbstractPlugin):
    def __init__(self, task, context):
        super(AddDNS, self).__init__()
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
            if self.is_active is True:
                content = 'nameserver {}\n'.format(self.ip)
                self.logger.debug('Created active dns content.')
            else:
                content = '#nameserver {}\n'.format(self.ip)
                self.logger.debug('Created passive dns content.')

            self.logger.debug('Writing to file...')
            self.write_file(self.dns_file, content, 'a')

            self.logger.info('NETWORK-MANAGER - ADD_DNS task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='DNS bilgisi başarıyla eklendi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    dns = AddDNS(task, context)
    dns.handle_task()
