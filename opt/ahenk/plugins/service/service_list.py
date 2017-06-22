#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class ServiceList(AbstractPlugin):
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

    def set_startup_service(self, service_name, action):
        (result_code, p_out, p_err) = self.execute('update-rc.d {0} {1}'.format(service_name, action))
        if result_code == 0:
            message = 'Service startup action was successful: {}'.format(service_name)
        else:
            message = 'Service action was unsuccessful: {0}, return code {1}'.format(service_name, str(result_code))

        self.logger.debug(message)
        return result_code, message

    def handle_task(self):
        self.logger.debug('Handling Service Task')
        try:
            items = (self.data)['serviceRequestParameters']
            resultMessage = ""
            for item in items:
                try:
                    if item['serviceStatus'] is not None and (
                            str(item['serviceStatus']) == 'Başlat' or str(item['serviceStatus']) == 'Start'):
                        resultcode, message = self.start_stop_service(str(item['serviceName']), "start")
                        resultMessage += message
                    if item['serviceStatus'] is not None and (
                            str(item['serviceStatus']) == 'Durdur' or str(item['serviceStatus']) == 'Stop'):
                        resultcode, message = self.start_stop_service(str(item['serviceName']), "stop")
                        resultMessage += message
                    if item['startAuto'] is not None and (
                            str(item['startAuto']) == 'Başlat' or str(item['startAuto']) == 'Start'):
                        resultcode, message = self.set_startup_service(str(item['serviceName']), "defaults")
                        resultMessage += message
                    if item['startAuto'] is not None and (
                            str(item['startAuto']) == 'Durdur' or str(item['startAuto']) == 'Stop'):
                        resultcode, message = self.set_startup_service(str(item['serviceName']), "remove")
                        resultMessage += message

                except Exception as e:
                    resultMessage += '{0} servisinin isteklerini gerçekleştirirken hata ile karşılaşıldı. Hata : {1}\r\n'.format(
                        str(item['serviceName']), str(e))
            self.logger.debug(resultMessage)
            data = {'ResultMessage': resultMessage}

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Servis istekleri gerçekleştirildi',
                                         data=json.dumps(data),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.debug('Service List Exception :' + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Servis istekleri gerçekleştirilirken beklenmedik hata!')


def handle_task(task, context):
    plugin = ServiceList(task, context)
    plugin.handle_task()
