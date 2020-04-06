#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>
# Author: Caner Feyzullahoglu <caner.feyzullahoglu@agem.com.tr>
"""
Style Guide is PEP-8
https://www.python.org/dev/peps/pep-0008/
"""

import json

from base.plugin.abstract_plugin import AbstractPlugin


class ScanNetwork(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()

        self.logger.debug('Initialized')
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.logger.debug('Creating nmap command')
        uuid = self.generate_uuid()
        self.file_path = self.Ahenk.received_dir_path() + uuid
        self.command = self.get_nmap_command()

    def handle_task(self):
        self.logger.debug('Handling task')
        try:
            self.logger.debug('Executing command: {0}'.format(self.command))
            result_code, p_out, p_err = self.execute(self.command)

            if result_code != 0:
                self.logger.error('Error occurred while executing nmap command')
                self.logger.error('Error message: {0}'.format(str(p_err)))
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='NETWORK INVENTORY Nmap komutu çalıştırılırken hata oluştu')
            else:
                self.logger.debug('Nmap command successfully executed')

                data = {}
                self.logger.debug('Getting md5 of file')
                md5sum = self.get_md5_file(str(self.file_path))

                self.logger.debug('{0} renaming to {1}'.format(self.file_path, md5sum))
                self.rename_file(self.file_path, self.Ahenk.received_dir_path() + md5sum)
                self.logger.debug('Renamed file.')

                data['md5'] = md5sum

                self.logger.debug('Creating response message')
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='NETWORK INVENTORY görevi başarıyla çalıştırıldı.',
                                             data=json.dumps(data),
                                             content_type=self.get_content_type().TEXT_PLAIN.value)

                self.logger.info('NETWORK INVENTORY task is handled successfully')
        except Exception as e:
            self.logger.error(
                'A problem occured while handling NETWORK INVENTORY task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK INVENTORY görevi çalıştırılırken bir hata oluştu.')

    def get_result(self, root):
        self.logger.debug('Parsing nmap xml output')
        result_list = {}
        index = 1

        for host in root.findall('host'):
            result = {}

            host_names = host.find('hostnames')
            ports = host.find('ports')
            os = host.find('os')
            distance = host.find('distance')
            status = host.find('status')
            self.logger.debug('STATUS: ++++++  ' + str(status))

            self.logger.debug('Getting hostname list')
            result['hostnames'] = self.get_hostname_list(host_names)
            self.logger.debug('Getting port list')
            result['ports'] = self.get_port_list(ports)
            self.logger.debug('Getting os list')
            result['os'] = self.get_os_list(os)
            self.logger.debug('Getting distance list')
            result['distance'] = self.get_distance(distance)
            self.logger.debug('Getting IP, MAC and MAC provider list')
            result['ipAddress'], result['macAddress'], result['macProvider'] = self.get_addresses(host)
            self.logger.debug('Getting status')
            result['status'] = self.get_status(host)

            result_list[index] = result
            index += 1

        return result_list

    def get_addresses(self, host):
        ip_address = ''
        mac_address = ''
        mac_provider = ''
        if host is not None:
            for address in host.findall('address'):
                if address.get('addrtype') == 'ipv4':
                    ip_address = address.get('addr')
                if address.get('addrtype') == 'mac':
                    mac_address = address.get('addr')
                    mac_provider = address.get('vendor')
        return ip_address, mac_address, mac_provider

    def get_hostname_list(self, hostnames):
        hostname_list = ''
        if hostnames is not None:
            for hostname in hostnames.findall('hostname'):
                name = hostname.get('name')
                if hostname_list != '':
                    hostname_list = hostname_list + ', ' + name
                else:
                    hostname_list = name

        return hostname_list

    def get_port_list(self, ports):
        port_list = ''
        if ports is not None:
            for port in ports.findall('port'):
                service = port.find('service')
                service_name = service.get('name')
                port_id = port.get('portid') + '/' + port.get('protocol') + ' ' + service_name
                if port_list != '':
                    port_list = port_list + ', ' + port_id
                else:
                    port_list = port_id

        return port_list

    def get_status(self, host):
        state = False
        if host is not None:
            for status in host.findall('status'):
                if status.get('state') == 'up':
                    state = True
                if status.get('state') == 'down':
                    state = False

        return state

    def get_os_list(self, os):
        os_list = ''
        if os is not None:
            for os_match in os.findall('osmatch'):
                name = os_match.get('name')
                if os_list != '':
                    os_list = os_list + ', ' + name
                else:
                    os_list = name

        return os_list

    def get_distance(self, distance):
        if distance is not None:
            return distance.get('value')
        return ''

    def get_nmap_command(self):
        command = 'nmap -v -oX'
        command += ' - ' + self.task['ipRange']
        if self.task['timingTemplate']:
            command += ' -T' + str(self.task['timingTemplate'])
        else:
            # average speed
            command += ' -T3'

        if self.task['ports']:
            command += ' -p' + self.task['ports']
        else:
            command += ' --top-ports 10'

        command += ' > ' + self.file_path

        return command


def handle_task(task, context):
    scan = ScanNetwork(task, context)
    scan.handle_task()
