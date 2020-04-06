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

            # get ports and ports information
            self.logger.debug('Fetch ports information')
            result_code, p_out, p_err = self.execute('ss -lntu | grep  \'tcp\|udp\' | awk \'{print $1,$5}\'')
            result_code_2, p_out_2, p_err_2 = self.execute(
                'cat /etc/services | grep \'/tcp\|/udp\' | awk \'{print $1,$2,$3,$4}\'')
            if p_err == "" and p_err_2 == "":
                list = ""
                for port_line in p_out.splitlines():
                    service_name = ""
                    port_line = str(port_line).split(" ")
                    port_type = port_line[0]
                    port_number = port_line[1][(str(port_line[1]).rfind(':') + 1):]
                    for service_line in p_out_2.splitlines():
                        service_line.replace("# ", "");
                        service_line = str(service_line).split(" ")
                        service_port = service_line[1].split("/")
                        if port_number == service_port[0]:
                            service_name = service_line[0]
                    if service_name == "":
                        service_name = "unknown"
                    port_info_str = service_name + " " + port_type + " " + port_number
                    if port_info_str.strip() not in list:
                        # check if port is blocked or not in iptables
                        result_code_3, p_out_3, p_err_3 = self.execute('sudo iptables -L')
                        is_port_blocked_input = False
                        is_port_blocked_output = False
                        state = "input"
                        if p_err_3 == "":
                            for ip_line in p_out_3.splitlines():
                                if ip_line in "Chain INPUT":
                                    state = "input"
                                if ip_line in "Chain OUTPUT":
                                    state = "output"

                                if state == "input" and "DROP" in ip_line and (
                                        "dpt:" + port_number in ip_line or "dpt:" + service_name in ip_line):
                                    is_port_blocked_input = True
                                if state == "output" and "DROP" in ip_line and (
                                        "dpt:" + port_number in ip_line or "dpt:" + service_name in ip_line):
                                    is_port_blocked_output = True
                        if is_port_blocked_input:
                            port_info_str += " Blocked"
                        else:
                            port_info_str += " Allowed"
                        if is_port_blocked_output:
                            port_info_str += " Blocked"
                        else:
                            port_info_str += " Allowed"

                        list += port_info_str.strip() + "\n"

                port = list.strip()

            self.logger.info('NETWORK-MANAGER task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ağ dosyaları başarıyla okundu.',
                                         data=json.dumps({'interfaces': interfaces, 'hosts': hosts, 'port': port, 'dns': dns,
                                                          'machine_hostname': machine_hostname}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occured while handling NETWORK-MANAGER task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK-MANAGER görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    ni = NetworkInformation(task, context)
    ni.handle_task()
