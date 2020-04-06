#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json


class SendMail(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            self.logger.debug("[RESOURCE USAGE] Send mail task is started.")
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='E posta gönderim bilgileri başarıyla iletildi',
                                         data=json.dumps(self.data), content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='e posta gönderim bilgileri edinilirken hata oluştu: {0}'.format(str(e)))


def handle_task(task, context):
    plugin = SendMail(task, context)
    plugin.handle_task()
