#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Hasan Kara <hasan.kara@pardus.org.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json


class GetFileContent(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            file_path = self.data['file-path']
            file_content = ""
            is_file_exists = False

            if self.is_exist(file_path):
                self.logger.info("File exists: " + file_path)
                is_file_exists = True
                # if the file size is less than 5K
                file_size = self.get_size(file_path) / 1024
                if file_size <= 5000:
                    file_content = self.read_file(file_path)
                    self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                                 message='Dosya içeriği başarıyla alındı..',
                                                 data=json.dumps({'file_exists': is_file_exists, 'file_content': file_content}),
                                                 content_type=self.get_content_type().APPLICATION_JSON.value)
                else:
                    self.logger.error("File size is too large. File Size: {0}K ".format(str(file_size)))
                    self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                 message='Dosya içeriği getirilemedi. Dosya boyutu çok büyük.',
                                                 content_type=self.get_content_type().APPLICATION_JSON.value)

            else:
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Dosya bulunamadı..',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Dosya içeriği alınırken hata oluştu: {0}'.format(str(e)))

def handle_task(task, context):
    plugin = GetFileContent(task, context)
    plugin.handle_task()
