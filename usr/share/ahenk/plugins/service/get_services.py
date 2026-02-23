#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from pystemd.systemd1 import Manager, Unit
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
            self.get_service_status()

            if self.is_exist(self.file_path):
                data = {}
                md5sum = self.get_md5_file(str(self.file_path))
                self.rename_file(self.file_path, self.Ahenk.received_dir_path() + '/' + md5sum)
                data['md5'] = md5sum
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Servis listesi başarıyla okundu.',
                                             data=json.dumps(data),
                                             content_type=self.get_content_type().TEXT_PLAIN.value)
            else:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Servis listesi getirilemedi')
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Servis listesi oluşturulurken hata oluştu: ' + str(e))

    def get_service_status(self):
        try:
            self.create_file(self.file_path)
            service_entries = []
            manager = Manager()
            manager.load()
            units = manager.Manager.ListUnits()
            for unit in units:
                unit_name = unit[0].decode()
                load_state = unit[2].decode()
                active_state = unit[3].decode()
                if not unit_name.endswith('.service') or load_state != 'loaded':
                    continue

                unit_proxy = Unit(unit_name.encode())
                unit_proxy.load()
                auto_state = unit_proxy.Unit.UnitFileState.decode()
                auto = 'enabled' if auto_state == 'enabled' else 'disabled'

                if active_state == 'active':
                    service_entries.append(
                        {
                            "serviceName": unit_name,
                            "serviceStatus": "active",
                            "startAuto": auto,
                        }
                    )
                else:
                    service_entries.append(
                        {
                            "serviceName": unit_name,
                            "serviceStatus": "inactive",
                            "startAuto": auto,
                        }
                    )

            payload = {
                "agent": self.Ahenk.dn(),
                "service_list": service_entries,
            }
            with open(self.file_path, 'w') as f:
                f.write(json.dumps(payload))

        except Exception as e:
            self.logger.error(str(e))


def handle_task(task, context):
    plugin = GetServices(task, context)
    plugin.handle_task()
