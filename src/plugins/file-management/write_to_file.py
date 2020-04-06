#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Hasan Kara <hasan.kara@pardus.org.tr>

from base.plugin.abstract_plugin import AbstractPlugin

class WriteToFile(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            file_path = self.data['file-path']
            file_content = self.data['file-content']

            if self.is_exist(file_path):
                self.write_file(file_path, file_content)
            else:
                path_str = ""
                for idx, folder in enumerate(file_path.split("/")):
                    if idx != len(file_path.split("/")) - 1:
                        path_str += folder + "/"
                (result_code, p_out, p_err) = self.execute("mkdir -p /" + path_str)

                if result_code == 0:
                    self.logger.error('Folders are created')
                else:
                    self.logger.error('Error occured while creating folders.')
                self.write_file(file_path, file_content)

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='İçerik dosyaya başarıyla yazıldı..',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='İçerik dosyaya yazılırken hata oluştu: {0}'.format(str(e)))


def handle_task(task, context):
    plugin = WriteToFile(task, context)
    plugin.handle_task()
