#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import fileinput
import re

from base.plugin.abstract_plugin import AbstractPlugin


class DeleteNetwork(AbstractPlugin):
    def __init__(self, task, context):
        super(DeleteNetwork, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.nic_file = '/etc/network/interfaces'

        self.type = self.task['type']
        self.name = self.task['name']
        self.is_active = self.task['is_active']

        if self.type == 'STATIC':
            self.ip = self.task['ip']
            self.netmask = self.task['netmask']
            self.gateway = self.task['gateway']

        self.content = ''

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            counter = 0
            for line in fileinput.input(self.nic_file, inplace=True):
                line = str(line).strip(" ")
                # to remove multiple spaces
                line = re.sub(' +', ' ', line)

                if not counter:
                    if self.type == 'static':
                        if self.is_active is True:
                            self.content = 'iface {0} inet static\n'.format(self.name)
                        else:
                            self.content = '#iface {0} inet static\n'.format(self.name)

                        if line.startswith(self.content):
                            counter = 3
                        else:
                            print(str(line).strip())

                    elif self.type == 'dhcp':
                        if self.is_active is True:
                            self.content = 'iface {} inet dhcp\n'.format(self.name)
                        else:
                            self.content = '#iface {} inet dhcp\n'.format(self.name)

                        if not line.startswith(self.content):
                            print(str(line).strip())

                    elif self.type == 'loopback':
                        if self.is_active is True:
                            self.content = 'iface {} inet loopback\n'.format(self.name)
                        else:
                            self.content = '#iface {} inet loopback\n'.format(self.name)

                        if not line.startswith(self.content):
                            print(str(line).strip())
                else:
                    counter -= 1

            self.logger.info('NETWORK-MANAGER - DELETE_NETWORK task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ağ arayüzü başarıyla silindi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    network = DeleteNetwork(task, context)
    network.handle_task()
