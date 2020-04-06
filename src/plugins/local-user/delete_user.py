#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin

class DeleteUser(AbstractPlugin):
    def __init__(self, task, context):
        super(DeleteUser, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.username = self.task['username']
        self.home = self.task['home']
        self.delete_home = self.task['delete_home']

        self.delete_user_home = 'rm -r {}'
        self.delete_user = 'userdel {}'
        self.logout_user = 'pkill -u {}'
        self.kill_all_process = 'killall -KILL -u {}'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            self.execute(self.logout_user.format(self.username))
            self.execute(self.kill_all_process.format(self.username))
            self.logger.debug('Killed all processes for {}'.format(self.username))

            if self.delete_home is True:
                self.execute(self.delete_user.format(self.username))
                self.execute(self.delete_user_home.format(self.home))
                self.logger.debug('Deleted user with home: {}'.format(self.username))
            elif self.delete_home is False:
                self.execute(self.delete_user.format(self.username))
                self.logger.debug('Deleted user: {}'.format(self.username))

            self.logger.info('User has been deleted successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Kullanıcı başarıyla silindi.')

        except Exception as e:
            self.logger.error(
                'A problem occured while handling Local-User task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Local-User görevi çalıştırılırken bir hata oluştu.')


def handle_task(task, context):
    delete_user = DeleteUser(task, context)
    delete_user.handle_task()
