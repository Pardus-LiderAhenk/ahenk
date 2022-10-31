#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin
import json


class GetUsbRules(AbstractPlugin):
    def __init__(self, task, context):
        super(GetUsbRules, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.whitelist_path = "/etc/udev/rules.d/99-ahenk-task-whitelist.rules"
        self.blacklist_path = "/etc/udev/rules.d/99-ahenk-task-blacklist.rules"
        self.usb_rule_list = []
 
    def handle_task(self):
        try:
            rule_type = "whitelist"
            if self.is_exist(self.whitelist_path):
                lines = self.read_file_by_line(self.whitelist_path)
                for line in lines:
                    self.get_usb_item(line, rule_type)

            if self.is_exist(self.blacklist_path):
                rule_type = "blacklist"
                lines = self.read_file_by_line(self.blacklist_path)
                for line in lines:
                    self.get_usb_item(line, rule_type)
            message = "İstemciye ait USB kuralları başarıyla alındı."
            if len(self.usb_rule_list) == 0:
                message = "İstemciye ait tanımlı USB kuralı bulunmamaktadır."

            self.logger.info('Get USB rule task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                        message=message,
                                        data=json.dumps({'usb_list': self.usb_rule_list, 'type': rule_type}),
                                        content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error('A problem occurred while getting USB rules. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                        message='USB kuralları getirilirken hata oluştu: {0}'.format(str(e)))
    
    def get_usb_item(self, line, type):
        line_parser_list = line.rstrip().split(', ')
        item_obj = {}
        authorized_str = 'ATTR{authorized}="1"'
        if type == "blacklist":
            authorized_str = 'ATTR{authorized}="0"'
        if authorized_str in line_parser_list:
            for item in line_parser_list:
                if "ATTR{manufacturer}" in item:
                    manufacturer = item.split("==")[1]
                    manufacturer = manufacturer.replace('"', '')
                    item_obj["vendor"] = manufacturer
                if "ATTR{product}" in item:
                    model = item.split("==")[1]
                    model = model.replace('"', '')
                    item_obj["model"] = model
                if "ATTR{serial}" in item:
                    serial_mumber = item.split("==")[1]
                    serial_mumber = serial_mumber.replace('"', '')
                    item_obj["serialNumber"] = serial_mumber
        if len(item_obj):
            self.usb_rule_list.append(item_obj)



def handle_task(task, context):
    manage = GetUsbRules(task, context)
    manage.handle_task()
