#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class GetGroups(AbstractPlugin):
    def __init__(self, task, context):
        super(GetGroups, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.command_get_groups = 'cut -d: -f1 /etc/group'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):

        try:
            result_code, p_out, p_err = self.execute(self.command_get_groups)
            groups = p_out.split('\n')
            groups.pop()

            self.logger.debug('groups: {0}'.format(groups))

            self.logger.info('Local User \'get_groups\' task is handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Grup listesi başarıyla getirildi.',
                                         data=json.dumps({'groups': groups}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occurred while handling Local-User \'get_groups\' task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Local-User \'get_groups\' görevi çalıştırılırken bir hata oluştu.')

def handle_task(task, context):
    get_groups = GetGroups(task, context)
    get_groups.handle_task()