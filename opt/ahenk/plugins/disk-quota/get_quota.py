#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class GetQuota(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.get_quota = 'repquota -a -s | tail -n +6 | awk \'{print $1,$4,$5,$6}\''

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:

            result_code, p_out, p_err = self.execute(self.get_quota)

            user_list = []
            lines = str(p_out).split('\n')

            for line in lines:
                detail = line.split(' ')

                if str(detail[0]).strip() is not None and str(detail[0]).strip() != '':
                    user = {'user': str(detail[0]).strip(), 'soft_quota': str(detail[1]).strip(),
                            'hard_quota': str(detail[2]).strip(), 'disk_usage': str(detail[3]).strip()}
                    user_list.append(user)

                    self.logger.debug(
                        'user: {0}, soft_quota: {1}, hard_quota: {2}, disk_usage: {3}'
                            .format(str(detail[0]).strip(), str(detail[1]).strip(), str(detail[2]).strip(),
                                    str(detail[3]).strip()))

            self.logger.info('DISK-QUOTA task is handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Kota bilgileri başarıyla alındı.',
                                         data=json.dumps({'users': user_list}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occured while handling DISK-QUOTA task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='DISK-QUOTA görevi uygulanırken bir hata oluştu.')


def handle_task(task, context):
    gq = GetQuota(task, context)
    gq.handle_task()
