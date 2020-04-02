#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class AddNetwork(AbstractPlugin):
    def __init__(self, task, context):
        super(AddNetwork, self).__init__()
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
            if self.type == 'STATIC':
                if self.is_active is True:
                    self.content = 'iface {0} inet static\n address {1}\n netmask {2}\n gateway {3}\n'.format(self.name,
                                                                                                              self.ip,
                                                                                                              self.netmask,
                                                                                                              self.gateway)
                else:
                    self.content = 'iface {0} inet static\n#address {1}\n#netmask {2}\n#gateway {3}\n'.format(self.name,
                                                                                                              self.ip,
                                                                                                              self.netmask,
                                                                                                              self.gateway)

                self.logger.debug('Created content for STATIC type.')
            elif self.type == 'DHCP':
                self.content = 'iface {} inet dhcp\n'.format(self.name)
                self.logger.debug('Created content for DHCP type.')
            elif self.type == 'LOOPBACK':
                self.content = 'iface {} inet loopback\n'.format(self.name)
                self.logger.debug('Created content for LOOPBACK type.')

            if self.is_active is False:
                self.logger.debug('Network interface is not active.')
                self.content = '#{}'.format(self.content)

            self.logger.debug('Writing to file...')
            self.write_file(self.nic_file, self.content, 'a')

            self.logger.info('NETWORK-MANAGER - ADD_NETWORK task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Yeni ağ arayüzü başarıyla eklendi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    network = AddNetwork(task, context)
    network.handle_task()
