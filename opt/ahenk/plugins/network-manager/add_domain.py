#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class AddDomain(AbstractPlugin):
    def __init__(self, task, context):
        super(AddDomain, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.dns_file = '/etc/resolv.conf'

        self.domain = self.task['domain']

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            content = 'domain {0}\nsearch {0}\n'.format(self.domain)

            self.logger.debug('Writing to file...')
            self.write_file(self.dns_file, content, 'a')

            self.logger.info('NETWORK-MANAGER - ADD_DOMAIN task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Alan adı bilgisi başarıyla eklendi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    domain = AddDomain(task, context)
    domain.handle_task()
