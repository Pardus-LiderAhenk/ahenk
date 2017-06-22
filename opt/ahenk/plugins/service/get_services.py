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
        self.service_status = 'service {} status'
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
            self.execute('echo { \\"service_list\\" :[ >> ' + self.file_path)
            self.isRecordExist = 1
        t_command = 'echo "{ \\"serviceName\\": \\"' + name + '\\", \\"serviceStatus\\": \\"' + status + '\\", \\"startAuto\\":\\"' + auto_start + '\\"}" >> ' + self.file_path
        self.execute(t_command)
        self.execute('echo , >> ' + self.file_path)

    def get_service_status(self):
        (result_code, p_out, p_err) = self.execute("service --status-all")
        self.create_file(self.file_path)
        # service_list = ServiceList()
        p_err = ' ' + p_err
        p_out = ' ' + p_out
        lines = p_out.split('\n')
        for line in lines:
            line_split = line.split(' ')
            if len(line_split) >= 5:
                proc = subprocess.Popen('chkconfig --list | grep 2:on | grep ' + line_split[len(line_split) - 1],
                                        shell=True)
                auto = "INACTIVE"
                name = line_split[len(line_split) - 1]

                if proc.wait() == 0:
                    auto = "ACTIVE"

                result, out, err = self.execute(self.service_status.format(name))

                if 'Unknown job' not in str(err):
                    if line_split[len(line_split) - 4] == '+':
                        self.add_file(name, "ACTIVE", auto)
                        # service_list.service_list.append(ServiceListItem(name, "ACTIVE", auto))
                    elif line_split[len(line_split) - 4] == '-':
                        self.add_file(name, "INACTIVE", auto)
                        # service_list.service_list.append(ServiceListItem(name, "INACTIVE", auto))
                else:
                    self.logger.debug(
                        'Service \'{0}\' has been not added to the list because of the its {1}'.format(name, err))

        line_err = p_err.split(',')

        for line in line_err:
            line_split = line.split(' ')
            if len(line_split) >= 6:
                proc = subprocess.Popen('chkconfig --list | grep 2:on | grep ' + line_split[len(line_split) - 1],
                                        shell=True)
                auto = "INACTIVE"
                if proc.wait() == 0:
                    auto = "ACTIVE"
                self.add_file(line_split[len(line_split) - 1], "unknown", auto)
                # service_list.service_list.append(ServiceListItem(line_split[len(line_split)-1], "unknown", auto))

        # result_service_list = json.dumps(service_list.__dict__, default=encode_service_object)
        # self.logger.debug('[SERVICE]' + 'Service list: ' + str(result_service_list))
        if self.isRecordExist == 1:
            self.execute("sed -i '$ d' " + self.file_path)
            self.execute('echo "]}" >> ' + self.file_path)


def handle_task(task, context):
    plugin = GetServices(task, context)
    plugin.handle_task()
