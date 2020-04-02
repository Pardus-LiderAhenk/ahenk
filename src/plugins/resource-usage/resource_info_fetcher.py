#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>
# Author: Emre Akkaya <emre.akkaya@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json


class ResourceUsage(AbstractPlugin):
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
            data = {'System': self.Os.name(), 'Release': self.Os.kernel_release(),
                    'Version': self.Os.distribution_version(), 'Machine': self.Os.architecture(),
                    'CPU Physical Core Count': self.Hardware.Cpu.physical_core_count(),
                    'Total Memory': self.Hardware.Memory.total(),
                    'Usage': self.Hardware.Memory.used(),
                    'Total Disc': self.Hardware.Disk.total(),
                    'Usage Disc': self.Hardware.Disk.used(),
                    'Processor': self.Hardware.Cpu.brand(),
                    'Device': device,
                    'CPU Logical Core Count': self.Hardware.Cpu.logical_core_count(),
                    'CPU Actual Hz': self.Hardware.Cpu.hz_actual(),
                    'CPU Advertised Hz': self.Hardware.Cpu.hz_advertised()
                    }
            self.logger.debug("Resource usage info gathered.")
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Anlık kaynak kullanım bilgisi başarıyla toplandı.',
                                         data=json.dumps(data), content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Anlık kaynak kullanım bilgisi toplanırken hata oluştu: {0}'.format(str(e)))


def handle_task(task, context):
    plugin = ResourceUsage(task, context)
    plugin.handle_task()
