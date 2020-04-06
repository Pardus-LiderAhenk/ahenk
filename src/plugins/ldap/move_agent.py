#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Edip YILDIZ
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>


from base.model.enum.content_type import ContentType
import json, threading


from base.plugin.abstract_plugin import AbstractPlugin

import threading


class MoveAgent(AbstractPlugin):
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



    def getCnFromDn(self,dn):
        if dn !=None and str(dn) !="":
            dnStrArr = str(dn).split(",")
            if len(dnStrArr)>0:
                return dnStrArr[0]


    def handle_task(self):
        try:
            dn = self.data['dn']
            newParentDn = self.data['newParentDn']

            jid= self.db_service.select_one_result('registration','jid','registered = 1')

            newDn=str(dn).replace(dn, self.getCnFromDn(dn)+ str(newParentDn))

            self.update_dn(jid,newDn)

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ahenk başarı ile taşındı.',
                                         data=json.dumps({'Dn': newDn}),
                                         content_type=ContentType.APPLICATION_JSON.value)


        except Exception as e:
            self.logger.error(" error on handle xmessage task. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ahenk taşınırken hata olustu' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)


def handle_task(task, context):
    cls = MoveAgent(task, context)
    cls.handle_task()
