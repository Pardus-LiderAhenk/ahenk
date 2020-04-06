#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import datetime

from base.plugin.abstract_plugin import AbstractPlugin


class LoginManager(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.command_logout_user = 'killall --user {0}'
        self.command_get_users_currently_login = "who | cut -d' ' -f1 | sort | uniq"

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:

            result_code, p_out, p_err = self.execute(self.command_get_users_currently_login)
            users = []

            if p_out != None:
                users = str(p_out).split('\n')
                users.pop()

            for user in users:
                self.logger.debug('End session for user: {0}'.format(user))
                self.execute(self.command_logout_user.format(user))

            self.logger.info('Login-Manager task is handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Oturumlar başarıyla sonlandırıldı.')

        except Exception as e:
            self.logger.error('A problem occured while handling Login-Manager task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Login-Manager görevi çalıştırılırken bir hata oluştu.')


def handle_task(task, context):
    manage = LoginManager(task, context)
    manage.handle_task()
