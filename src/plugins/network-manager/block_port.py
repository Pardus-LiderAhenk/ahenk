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

        self.ports = self.task['ports']

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            self.logger.debug('Writing to iptables ...')
            for port in self.ports.split(' '):
                self.execute('iptables -A INPUT -p tcp --dport ' + port + ' -m state --state NEW,ESTABLISHED -j DROP')
                self.execute('iptables -A OUTPUT -p tcp --dport ' + port + ' -m state --state NEW,ESTABLISHED -j DROP')

            self.execute('iptables-save')

            self.logger.info('NETWORK-MANAGER - Blocking Ports: ' + self.ports + ' are handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Portlar başarıyla engellendi')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    domain = AddDomain(task, context)
    domain.handle_task()
