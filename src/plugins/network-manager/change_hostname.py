#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class ChangeHostname(AbstractPlugin):
    def __init__(self, task, context):
        super(ChangeHostname, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.hostname_file = '/etc/hostname'

        self.hostname = self.task['hostname']

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            content = '{}\n'.format(self.hostname)

            self.logger.debug('[NETWORK-MANAGER - ADD_HOST] Writing to file...')
            self.write_file(self.hostname_file, content)

            self.logger.info('NETWORK-MANAGER - CHANGE_HOSTNAME task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Sunucu ismi başarıyla değiştirildi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    hostname = ChangeHostname(task, context)
    hostname.handle_task()
