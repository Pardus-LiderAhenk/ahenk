#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class ShutDownMachine(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.shut_down_command = 'sleep 5s; shutdown -h now'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            self.logger.debug('Shutting down the machine...')
            self.execute(self.shut_down_command, result=False)

            response = 'Shutdown komutu başarıyla çalıştırıldı. Bilgisayar kapatılacak. Mac Adres(ler)i: {0}, Ip Adres(ler)i: {1}' \
                .format(self.Hardware.Network.mac_addresses(), self.Hardware.Network.ip_addresses())

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message=response)
            self.logger.info('WOL task is handled successfully')

        except Exception as e:
            self.logger.error('A problem occured while handling WOL task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='WOL görevi uygulanırken bir hata oluştu: {0}'.format(str(e)))


def handle_task(task, context):
    shut_down = ShutDownMachine(task, context)
    shut_down.handle_task()
