#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class AddHost(AbstractPlugin):
    def __init__(self, task, context):
        super(AddHost, self).__init__()
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
            if self.is_active is True:
                content = '{0} {1}\n'.format(self.ip, self.hostname)
                self.logger.debug('Created active host content.')
            else:
                content = '#{0} {1}\n'.format(self.ip, self.hostname)
                self.logger.debug('Created passive host content.')

            self.logger.debug('Writing to file...')
            self.write_file(self.hosts_file, content, 'a')

            self.logger.info('NETWORK-MANAGER - ADD_HOST task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Sunucu bilgisi başarıyla eklendi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    host = AddHost(task, context)
    host.handle_task()
