#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class DeleteUsbRule(AbstractPlugin):
    def __init__(self, task, context):
        super(DeleteUsbRule, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.whitelist_path = "/etc/udev/rules.d/99-ahenk-task-whitelist.rules"
        self.blacklist_path = "/etc/udev/rules.d/99-ahenk-task-blacklist.rules"
 
    def handle_task(self):
        try:
            ruleIsExist = False
            message = "İstemciye ait USB kuralları başarıyla silindi."
            if self.is_exist(self.whitelist_path):
                self.delete_file(self.whitelist_path)
                ruleIsExist = True
 
            if self.is_exist(self.blacklist_path):
                self.delete_file(self.blacklist_path)
                ruleIsExist = True
            
            if ruleIsExist:
                message = "İstemciye ait USB kuralları başarıyla silindi."
                self.execute('udevadm control --reload-rules')
                self.logger.debug('Blacklist/Whitelist was reloaded.')
            else:
                message = "İstemciye ait tanımlı USB kuralı bulunmamaktadır."

            self.logger.info('USB rule task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message=message)
        except Exception as e:
            self.logger.error('A problem occurred while deleting USB rules. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='USB kuralları silinirken hata oluştu: {0}'.format(str(e)))


def handle_task(task, context):
    manage = DeleteUsbRule(task, context)
    manage.handle_task()
