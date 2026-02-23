#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
from base.plugin.abstract_plugin import AbstractPlugin
from base.model.enum.desktop_type import DisplayManagerUser

class LoginManager(AbstractPlugin):
    def __init__(self, task, context):
        super(LoginManager, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.command_logout_user = 'loginctl terminate-user {0}'
        self.command_get_users = "loginctl list-users --no-legend | awk '{print $2}'"
        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            result_code, p_out, p_err = self.execute(self.command_get_users)
            excluded_users = DisplayManagerUser.all_users()
            users = []

            if p_out:
                raw_users = p_out.strip().splitlines()
                users = [u.strip() for u in raw_users]

            users = [user for user in users if user not in excluded_users]
            if not users:
                self.logger.info("No active users found to logout.")
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Sonlandırılacak aktif oturum bulunamadı.')
                return

            killed_count = 0
            for user in users:
                user = user.strip()
                if user not in excluded_users:
                    self.logger.debug('Terminating session for user: {0}'.format(user))
                    self.execute(self.command_logout_user.format(user))
                    killed_count += 1

            self.logger.info('Login-Manager task is handled successfully. Total users logged out: {0}'.format(killed_count))
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='{0} adet kullanıcının oturumu başarıyla sonlandırıldı.'.format(killed_count))

        except Exception as e:
            self.logger.error('A problem occured while handling Login-Manager task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Login-Manager görevi çalıştırılırken bir hata oluştu: ' + str(e))


def handle_task(task, context):
    manage = LoginManager(task, context)
    manage.handle_task()