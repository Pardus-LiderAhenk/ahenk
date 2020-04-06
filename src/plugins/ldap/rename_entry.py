#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Edip YILDIZ
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>


from base.model.enum.content_type import ContentType
import json, threading


from base.plugin.abstract_plugin import AbstractPlugin

import threading


class UpdateEntry(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()



    def update_dn(self, jid, newDn):
        cols = ['dn'];
        values = [newDn]
        return self.db_service.update('registration', cols, values, 'jid=\''+jid+'\'')


    def handle_task(self):
        try:
            dn = self.data['dn']
            jid= self.db_service.select_one_result('registration','jid','registered = 1')

            cn = self.data['oldCn']
            newCn = self.data['newCn']

            newDn=str(dn).replace(cn,newCn)

            self.update_dn(jid,newDn)

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ahenk adı başarı ile değiştirildi.',
                                         data=json.dumps({'Dn': newDn}),
                                         content_type=ContentType.APPLICATION_JSON.value)


        except Exception as e:
            self.logger.error(" error on handle xmessage task. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ahenk adı değiştirilirken hata olustu' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)


def handle_task(task, context):
    cls = UpdateEntry(task, context)
    cls.handle_task()
