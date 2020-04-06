#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json
import subprocess
from base.plugin.abstract_plugin import AbstractPlugin


class ServiceList(object):
    def __init__(self):
        self.service_list = []


class ServiceListItem:
    def __init__(self, service_name, status, auto):
        self.serviceName = service_name
        self.serviceStatus = status
        self.startAuto = auto


def encode_service_object(obj):
    if isinstance(obj, ServiceListItem):
        return obj.__dict__
    return obj


class GetServices(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.temp_file_name = str(self.generate_uuid())
        self.file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)
        self.service_status = 'systemctl status {}'
        self.isRecordExist = 0

    def handle_task(self):
        try:
            self.logger.debug('Executing command for service list.')
            self.get_service_status()

            self.logger.debug('Command executed.')

            if self.is_exist(self.file_path):
                data = {}
                self.logger.debug(str(self.file_path))
                md5sum = self.get_md5_file(str(self.file_path))
                self.logger.debug('{0} renaming to {1}'.format(self.temp_file_name, md5sum))
                self.rename_file(self.file_path, self.Ahenk.received_dir_path() + '/' + md5sum)
                self.logger.debug('Renamed.' + self.Ahenk.received_dir_path() + '/' + md5sum)
                data['md5'] = md5sum
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Servis listesi başarıyla okundu.',
                                             data=json.dumps(data),
                                             content_type=self.get_content_type().TEXT_PLAIN.value)
                self.logger.debug("Execution Info fetched succesfully. ")
                self.logger.debug("Execution Info has sent")
            else:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Servis listesi getirilemedi')
            self.logger.debug('Service list created successfully')
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Servis listesi oluşturulurken hata oluştu: ' + str(e))

    def add_file(self, name, status, auto_start):
        if self.isRecordExist == 0:
            self.execute('echo { \\"agent\\" : \\"'+ self.Ahenk.dn() + '\\", \\"service_list\\" :[ >> ' + self.file_path)
            self.isRecordExist = 1
        t_command = 'echo "{ \\"serviceName\\": \\"' + name + '\\", \\"serviceStatus\\": \\"' + status + '\\", \\"startAuto\\":\\"' + auto_start + '\\"}" >> ' + self.file_path
        self.execute(t_command)
        self.execute('echo , >> ' + self.file_path)

    def add_agentDnToFile(self):
        t_command = 'echo "{ \\"agent\\": \\"' + self.Ahenk.dn() +'\\"}" >> ' + self.file_path
        self.execute(t_command)
        self.execute('echo , >> ' + self.file_path)

    def get_service_status(self):
        try:
            (result_code, p_out, p_err) = self.execute("systemctl list-units --type service --all | grep loaded")
            self.create_file(self.file_path)
            # service_list = ServiceList()
            lines = p_out.split('\n')
            for line in lines:
                line_split = line.split(' ')
                service=[]
                for word in line_split:
                    if word != '' :
                        service.append(word)
                if len(service)>0 and '.service' not in service[0]:
                    del service[0]

                if len(service)>0 and '.service' in service[0]: # service[0] = service name, service[1] is loaded, service[2] active or not,
                    result, out, err = self.execute(self.service_status.format(service[0])) # check service is enable or not on auto start
                    auto='INACTIVE'
                    if 'disabled' in out:
                        auto='INACTIVE'
                    elif 'enabled' in out:
                        auto='ACTIVE'

                    if service[2] == 'active':
                        self.add_file(service[0], "ACTIVE", auto)
                    else:
                        self.add_file(service[0], 'INACTIVE',auto)

                    print(service)


            if self.isRecordExist == 1:
                self.execute("sed -i '$ d' " + self.file_path)
                self.execute('echo "]}" >> ' + self.file_path)

        except Exception as e:
            print(str(e))
            self.logger.error(str(e))




def handle_task(task, context):
    plugin = GetServices(task, context)
    plugin.handle_task()
