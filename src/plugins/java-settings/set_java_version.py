#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from base.plugin.abstract_plugin import AbstractPlugin

class SetJavaVersion(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        
    def handle_task(self):
        try:
            java_name = self.task.get('javaName')

            if ' ' in java_name or '\t' in java_name or '\n' in java_name:
                self.logger.warning(f'Invalid Jdk name: {repr(java_name)}')
                return False
            
            if not java_name:
                self.context.create_response(
                    code=self.message_code.TASK_ERROR.value,
                    message='Java versiyonu belirtilmedi.',
                    content_type=self.get_content_type().APPLICATION_JSON.value
                )
                return
                        
            command = f'/usr/sbin/update-java-alternatives --set {java_name}'
            result_code, p_out, p_err = self.execute(command)
            
            if result_code != 0:
                self.logger.error(f'Error setting Java version: {p_err}')
                self.context.create_response(
                    code=self.message_code.TASK_ERROR.value,
                    content_type=self.get_content_type().APPLICATION_JSON.value,
                    message=f'Java versiyonu ayarlanırken hata oluştu: {p_err}',
                    data=json.dumps({'error': str(p_err)})
                )
                return
            
            self.logger.info(f'Successfully set Java version to: {java_name}')
            self.context.create_response(
                code=self.message_code.TASK_PROCESSED.value,
                content_type=self.get_content_type().APPLICATION_JSON.value,
                message=f'{java_name} başarıyla varsayılan Java versiyonu olarak ayarlandı.',
                data=json.dumps({
                    'javaName': java_name,
                    'output': p_out
                }),
            )
            
        except Exception as e:
            self.logger.error(f'Exception in set_java_version: {str(e)}')
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                content_type=self.get_content_type().APPLICATION_JSON.value,
                message=f'Java versiyonu ayarlanırken hata oluştu: {str(e)}'
            )


def handle_task(task, context):
    plugin = SetJavaVersion(task, context)
    plugin.handle_task()