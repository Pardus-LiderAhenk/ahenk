#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json


class ServiceManagement(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def start_stop_service(self, service_name, service_action):
        (result_code, p_out, p_err) = self.execute('service {0} {1}'.format(service_name, service_action))
        if result_code == 0:
            message = 'Service start/stop action was successful: '.format(service_action)

        else:
            message = 'Service action was unsuccessful: {0}, return code {1}'.format(service_action, str(result_code))

        self.logger.debug(message)
        return result_code, message

    def set_startup_service(self, service_name):
        (result_code, p_out, p_err) = self.execute('update-rc.d {} defaults'.format(service_name))

        if result_code == 0:
            message = 'Service startup action was successful: {}'.format(service_name)
        else:
            message = 'Service action was unsuccessful: {0}, return code {1}'.format(service_name, str(result_code))

        self.logger.debug('SERVICE' + message)
        return result_code, message

    def handle_task(self):
        try:
            self.logger.debug("Service Management task is started.")
            service_name = str((self.data)['serviceName'])
            service_status = str((self.data)['serviceStatus'])
            start_auto = bool((self.data)['startAuto'])
            if service_status == 'Start' or service_status == 'Başlat':
                service_action = 'start'
            else:
                service_action = 'stop'
            result_code, message = self.start_stop_service(service_name, service_action)
            if result_code == 0 and start_auto is True:
                result_code, message = self.set_startup_service(service_name)
            if result_code == 0:
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Servis başlatma/durdurma/otomatik başlatma işlemi başarıyla gerçekleştirildi',
                                             data=json.dumps(self.data),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                self.context.create_response(code=self.message_code.TASK_ERROR.value, message=message)

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Servis başlatma/durdurma/otomatik başlatma işlemi sırasında bir hata oluştu: {0}'.format(
                                             str(e)))


def handle_task(task, context):
    plugin = ServiceManagement(task, context)
    plugin.handle_task()
