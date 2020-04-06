#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>
## shutdown agents

from base.plugin.abstract_plugin import AbstractPlugin

class LoginManager(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.command_shutdown = 'shutdown -h now'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            result_code, p_out, p_err = self.execute(self.command_shutdown)
            self.logger.info("shutdown agent success")
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='İstemci başarıyla kapatıldı.')
        except Exception as e:
            self.logger.error('A problem occured while handling Login-Manager task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='İstemci kapatılırken bir hata oluştu.')

def handle_task(task, context):
    manage = LoginManager(task, context)
    manage.handle_task()
