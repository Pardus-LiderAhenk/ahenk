#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class NetworkInformation(AbstractPlugin):
    def __init__(self, task, context):
        super(NetworkInformation, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.nic_file = '/etc/network/interfaces'
        self.hosts_file = '/etc/hosts'
        self.dns_file = '/etc/resolv.conf'
        self.hostname_file = '/etc/hostname'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            interfaces = self.read_file(self.nic_file)
            self.logger.debug('Read interfaces file.')

            hosts = self.read_file(self.hosts_file)
            self.logger.debug('Read hosts file.')

            dns = self.read_file(self.dns_file)
            self.logger.debug('Read dns file.')

            machine_hostname = self.read_file(self.hostname_file)
            self.logger.debug('Read hostname file.')

            self.logger.info('NETWORK-MANAGER task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ağ dosyaları başarıyla okundu.',
                                         data=json.dumps({'interfaces': interfaces, 'hosts': hosts, 'dns': dns,
                                                          'machine_hostname': machine_hostname}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    ni = NetworkInformation(task, context)
    ni.handle_task()
