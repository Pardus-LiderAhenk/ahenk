#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <hasankara@pardus.org.tr>

from base.model.enum.content_type import ContentType
import json

from base.scope import Scope
from base.plugin.abstract_plugin import AbstractPlugin
from base.registration.registration import Registration


class DeleteAgent(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        scope = Scope.get_instance()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            dn = self.data['dn']
            directory_server = self.data['directory_server']
            registration = Scope.get_instance().get_registration()
            registration.purge_and_unregister(directory_server)

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ahenk başarı ile silindi.',
                                         data=json.dumps({'Dn': dn}),
                                         content_type=ContentType.APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error(" error on handle deleting agent. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ahenk silinirken hata olustu' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)


def handle_task(task, context):
    cls = DeleteAgent(task, context)
    cls.handle_task()

