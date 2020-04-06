#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import re

from base.plugin.abstract_plugin import AbstractPlugin


class DeleteDomain(AbstractPlugin):
    def __init__(self, task, context):
        super(DeleteDomain, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.dns_file = '/etc/resolv.conf'

        self.domain = self.task['domain']

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            lines = self.read_file_by_line(self.dns_file)
            f = open(self.dns_file, "w")

            for line in lines:
                line = str(line).strip(" ")
                # to remove multiple spaces
                line = re.sub(' +', ' ', line)

                if line != 'domain {}\n'.format(self.domain) and line != 'search {}\n'.format(self.domain):
                    self.logger.debug(
                        'Writing a line to dns file... Line: {}'.format(line))
                    f.write(line)
                else:
                    self.logger.debug(
                        'Line has been deleted from dns file. Line: {}'.format(line))

            f.close()

            self.logger.info('NETWORK-MANAGER - DELETE_DOMAIN task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Alan adı bilgisi başarıyla silindi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    domain = DeleteDomain(task, context)
    domain.handle_task()
