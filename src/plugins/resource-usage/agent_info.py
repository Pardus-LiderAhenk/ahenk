#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin
from base.system.disk_info import DiskInfo
import json


class AgentInfo(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            device = ""
            self.logger.debug("Gathering resource usage for disk, memory and CPU.")
            for part in self.Hardware.Disk.partitions():
                if len(device) != 0:
                    device += ", "
                device = device + part.device

            ssd_list, hdd_list = DiskInfo.get_all_disks()

            data = {'System': self.Os.name(), 'Release': self.Os.kernel_release(),
                    'agentVersion': self.get_agent_version(),
                    'hostname': self.Os.hostname(),
                    'ipAddresses': str(self.Hardware.Network.ip_addresses()).replace('[', '').replace(']', ''),
                    'os.name': self.Os.name(),
                    'osVersion': self.Os.version(),
                    'macAddresses': str(self.Hardware.Network.mac_addresses()).replace('[', '').replace(']', ''),
                    'hardware.systemDefinitions': self.Hardware.system_definitions(),
                    'hardware.monitors': self.Hardware.monitors(),
                    'hardware.screens': self.Hardware.screens(),
                    'hardware.usbDevices': self.Hardware.usb_devices(),
                    'hardware.printers': self.Hardware.printers(),
                    'diskTotal': self.Hardware.Disk.total(),
                    'diskUsed': self.Hardware.Disk.used(),
                    'diskFree': self.Hardware.Disk.free(),
                    'memory': self.Hardware.Memory.total(),
                    'Device': device,
            }

            if len(ssd_list) > 0:
                data['hardwareDiskSsdInfo'] = str(ssd_list)

            if len(hdd_list) > 0:
                data['hardwareDiskHddInfo'] = str(hdd_list)

            self.logger.debug("Agent info gathered.")
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ahenk bilgileri başarıyla güncellendi.',
                                         data=json.dumps(data), content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ahenk bilgileri güncellenirken hata oluştu: {0}'.format(str(e)))


def handle_task(task, context):
    plugin = AgentInfo(task, context)
    plugin.handle_task()
