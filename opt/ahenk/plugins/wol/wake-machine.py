#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import time

from base.plugin.abstract_plugin import AbstractPlugin


class WakeMachine(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.mac_address_list = self.task['macAddress']
        self.ip_address_list = self.task['ipAddress']
        self.port_list = self.task['port']
        self.time_list = self.task['time']

        self.wake_command = 'wakeonlan {}'
        self.port_control = 'nmap -p {0} {1} | grep {2}/tcp'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            result_list = []
            is_open = None

            if self.mac_address_list:

                for i, val in enumerate(self.mac_address_list):
                    mac_addresses = str(val).split(',')
                    for j, mac in enumerate(mac_addresses):
                        mac = mac.replace("'", "")

                        for _ in range(5):
                            self.logger.debug('Sending magic package to: {}'.format(mac))
                            result_code_wake, p_out_wake, p_err_wake = self.execute(self.wake_command.format(mac))

                            if p_err_wake != '':
                                self.logger.debug(
                                    'An error occured while sending magic package. Mac Address: {}'.format(mac))
                                raise Exception(p_err_wake)

                    time.sleep(int(self.time_list[i]))

                    is_open = False

                    if self.ip_address_list:
                        ip_addresses = str(self.ip_address_list[i]).split(',')

                        if self.port_list:
                            ports = str(self.port_list[i]).split(',')
                            for j, ip in enumerate(ip_addresses):
                                for port in ports:
                                    self.logger.debug('Scanning the port. Port: {0}, IP: {1}'.format(port, ip))
                                    result_code, out, err = self.execute(self.port_control.format(port, ip, port))

                                    if err != '':
                                        self.logger.debug(
                                            'An error occured while scanning the port. Mac Address(es): {0}, Ip Address: {1}, Port: {2}'.format(
                                                val, ip, port))

                                    if 'open' in out:
                                        self.logger.debug(
                                            'Machine is awake. Mac Address(es): {0}, Ip Address: {1}, Port: {2}'.format(
                                                val, ip, port))
                                        result_list.append(
                                            'Bilgisayar açık. Mac Adres(ler)i: {0}, Ip Adres(ler)i: {1}, Port: {2}'.format(
                                                val, ip, port))
                                        is_open = True
                        else:
                            self.logger.debug('Port list is empty! Waking control could not be done!')
                    else:
                        self.logger.debug('Ip address list is empty! Waking control could not be done!')

                    if is_open == False:
                        self.logger.debug('The machine is not awake or ip adresses are wrong ' \
                                          'or ports are close. Mac Address(es): {0}, Ip Address(es): {1}, Port(s): {2}'.format(
                            val, self.ip_address_list[i], self.port_list[i]))
                        result_list.append('Bilgisayar açık değil, belirtilen ip adresleri yanlış ya da ' \
                                           'portlar kapalı. Mac Adres(ler)i: {0}, Ip Adres(ler)i: {1}, Port(lar): {2}'.format(
                            val, self.ip_address_list[i], self.port_list[i]))

                response = ' - '.join(result_list)
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message=response)
                self.logger.info('WOL task is handled successfully')

            else:
                raise Exception('Mac address list is empty!')

        except Exception as e:
            self.logger.error('A problem occured while handling WOL task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='WOL görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    wake = WakeMachine(task, context)
    wake.handle_task()
