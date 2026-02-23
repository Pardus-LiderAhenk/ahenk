#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from base.plugin.abstract_plugin import AbstractPlugin

class UsbRule(AbstractPlugin):
    def __init__(self, task, context):
        super(UsbRule, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.logger.info("---->>> "+ str(self.task))
        self.script = '/bin/bash ' + self.Ahenk.plugins_path() + 'usb/scripts/{0}'
        self.script_path = self.Ahenk.plugins_path() + 'usb/scripts/{0}'
        self.items = []
        self.command_vendor = "grep -lw '{0}' /sys/bus/usb/devices/*/manufacturer | grep -o -P '.{{0,}}/.{{0,0}}'"
        self.command_model = "grep -lw '{0}' {1}product"
        self.command_serial = "grep -lw '{0}' {1}serial"
        self.command_authorized = "echo '{0}' > {1}authorized"
        self.command_serial_is_exist = 'if test -e {0}serial; then echo "exist"; else echo "not found"; fi'
        self.logger.debug('Parameters were initialized.')
        self.whitelist_path = "/etc/udev/rules.d/99-ahenk-task-whitelist.rules"
        self.blacklist_path = "/etc/udev/rules.d/99-ahenk-task-blacklist.rules"

    def handle_task(self):
        try:
            if self.has_attr_json(self.task, 'items') is True:
                self.items = self.task['items']
                self.logger.debug('Blacklist/Whitelist will be created task.')
                if self.has_attr_json(self.task, 'type') is True:
                    self.logger.debug('BlackList Whitelist will be created....')
                    self.create_blacklist_whitelist()
            self.logger.info('USB rule task is handled successfully.')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='İstemciye ait USB kuralları başarıyla güncellendi.')
        except Exception as e:
            self.logger.error('A problem occurred while handling USB rule task. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='İstemciye ait USB kuralların uygulanırken bir hata oluştu: {0}'.format(str(e)))

    def organize_rule_files(self, is_whitelist):
        if is_whitelist == 0:
            if self.is_exist(self.whitelist_path):
                self.delete_file(self.whitelist_path)
            self.execute('echo "# Ahenk Blacklist Rules" > {0}'.format(self.blacklist_path))
        else:
            if self.is_exist(self.blacklist_path):
                self.delete_file(self.blacklist_path)
            self.execute('echo "# Ahenk Whitelist Rules" > {0}'.format(self.whitelist_path))

    def write_whitelist_line(self, vendor, model, serial_number):
        rule = 'ACTION=="add|change", SUBSYSTEM=="usb", '

        if vendor and len(vendor) > 0:
            rule += 'ATTRS{manufacturer}=="' + vendor + '", '
        if model and len(model) > 0:
            rule += 'ATTRS{product}=="' + model + '", '
        if serial_number and len(serial_number) > 0:
            rule += 'ATTRS{serial}=="' + serial_number + '", '
        
        rule += 'ENV{AHENK_OK}="1"'

        self.execute("echo '{0}' >> {1}".format(rule, self.whitelist_path))

    def write_rule_line(self, command):
        p_result_code, p_out, p_err = self.execute(command)
        if p_result_code == 0:
            self.logger.debug('Rule line is added successfully')
        elif p_result_code != 0:
            self.logger.debug('Error while adding rule line to /etc/udev/rules.d/ , Error message : {0}'.format(p_err))

    def create_rule_line(self, vendor, model, serial_number, is_whitelist):
        if is_whitelist == 0:
            command_blackandwhitelist = 'echo ' + "'" + 'ACTION ==\"add|change\", SUBSYSTEM==\"usb\", '
            if vendor is not None and len(vendor) > 0:
                command_blackandwhitelist += 'ATTR{manufacturer}==\"' + vendor + '\", '
            if model is not None and len(model) > 0:
                command_blackandwhitelist += 'ATTR{product}==\"' + model + '\", '
            if serial_number is not None and len(serial_number) > 0:
                command_blackandwhitelist += 'ATTR{serial}==\"' + serial_number + '\", '
            command_blackandwhitelist += 'ATTR{authorized}=\"0\"' + "'" + '>> {0}'.format(self.blacklist_path)
            self.write_rule_line(command_blackandwhitelist)
        else:
            self.write_whitelist_line(vendor, model, serial_number)

    def create_blacklist_whitelist(self):
        self.logger.debug('usb storage will be enabled')
        self.execute(self.script.format('ENABLED_usbstorage.sh'), result=True)
        self.logger.debug('usb storage enabled')
        if self.task['type'] == 'blacklist':
            is_whitelist = 0
        else:
            is_whitelist = 1
        self.logger.debug('Rule files are organizing....')
        self.organize_rule_files(is_whitelist)
        self.logger.debug('Rule files are organized')

        for item in self.items:
            item_parameters = json.loads(str(json.dumps(item)))
            vendor = item_parameters.get('vendor', '')
            model = item_parameters.get('model', '')
            serial_number = item_parameters.get('serialNumber', '')

            self.create_rule_line(vendor, model, serial_number, is_whitelist)

            self.logger.debug('vendor, model and serial number is set....')
            self.apply_immediate_scan_logic(vendor, model, serial_number, is_whitelist) 

        if is_whitelist == 1:
            allow_whitelist = 'ACTION=="add|change", SUBSYSTEM=="usb", ENV{AHENK_OK}=="1", ATTR{authorized}="1"'
            self.execute("echo '{0}' >> {1}".format(allow_whitelist, self.whitelist_path))

            # HID (mouse / keyboard)
            hid_rule = 'ACTION=="add|change", SUBSYSTEM=="usb", ATTR{bInterfaceClass}=="03", ATTR{authorized}="1"'
            self.execute("echo '{0}' >> {1}".format(hid_rule, self.whitelist_path))

            block_storage = 'ACTION=="add|change", SUBSYSTEM=="usb", ENV{AHENK_OK}!="1", ATTR{bInterfaceClass}=="08", ATTR{authorized}="0"'
            self.execute("echo '{0}' >> {1}".format(block_storage, self.whitelist_path))

        self.execute('udevadm control --reload-rules')
        self.logger.debug('Blacklist/Whitelist was created.')

    def apply_immediate_scan_logic(self, vendor, model, serial_number, is_whitelist):
        self.logger.debug('Scanning immediate devices for vendor: {0}, model: {1}'.format(vendor, model))

        result_code, p_out, p_err = self.execute(self.command_vendor.format(vendor), result=True)
        folder_list = str(p_out).split('\n')
        if len(folder_list) > 0 and folder_list[-1] == '': 
            folder_list.pop()

        if p_out == '' and vendor != '':
            self.logger.debug('Device has not been found because of vendor. Vendor: {0}'.format(vendor))

        if vendor == '':
            folder_list = []
            folder_list.append('/sys/bus/usb/devices/*/')

        for folder in folder_list:
            result_code, p_out, p_err = self.execute(self.command_model.format(model, folder), result=True)

            if p_out == '' and model != '':
                self.logger.debug('Device model not found in: {0}'.format(folder))
            else:
                model_folder_list = str(p_out).split('\n')
                if len(model_folder_list) > 0 and model_folder_list[-1] == '': 
                    model_folder_list.pop()

                if p_out == '':
                    model_folder_list.append(folder)

                if vendor == '' and model == '':
                    model_folder_list = []
                    model_folder_list.append('/sys/bus/usb/devices/*/')

                for model_folder in model_folder_list:
                    if 'product' in model_folder:
                        model_folder = model_folder.strip('product')

                    if model_folder != '/sys/bus/usb/devices/*/':
                        result_code, p_out, p_err = self.execute(self.command_serial_is_exist.format(model_folder), result=True)
                        p_out_exist = p_out
                    else:
                        p_out_exist = "path_generic"

                    if 'exist' in str(p_out_exist) or model_folder == '/sys/bus/usb/devices/*/':
                        result_code, p_out, p_err = self.execute(self.command_serial.format(serial_number, model_folder), result=True)
                        
                        serial_folder_list = []
                        if p_out == '' and serial_number != '':
                            self.logger.debug('Serial mismatch in directory: {0}'.format(model_folder))
                        else:
                            serial_folder_list = str(p_out).split('\n')
                            if len(serial_folder_list) > 0 and serial_folder_list[-1] == '': 
                                serial_folder_list.pop()

                            if p_out == '':
                                serial_folder_list.append(model_folder)

                            for serial_folder in serial_folder_list:
                                serial_folder = serial_folder.strip('serial')
                                
                                if is_whitelist == 1:
                                    self.execute(self.command_authorized.format('1', serial_folder), result=True)
                                    self.logger.debug('IMMEDIATE: Enabled device at {0}'.format(serial_folder))
                                else:
                                    self.execute(self.command_authorized.format('0', serial_folder), result=True)
                                    self.logger.debug('IMMEDIATE: Disabled device at {0}'.format(serial_folder))

                    elif 'not found' in str(p_out_exist):
                        dir_path = ''
                        if model != '':
                            dir_path = model_folder
                        elif vendor != '':
                            dir_path = folder

                        if dir_path != '':
                            if is_whitelist == 1:
                                self.execute(self.command_authorized.format('1', dir_path), result=True)
                                self.logger.debug('IMMEDIATE: Enabled device (No Serial) at {0}'.format(dir_path))
                            else:
                                self.execute(self.command_authorized.format('0', dir_path), result=True)
                                self.logger.debug('IMMEDIATE: Disabled device (No Serial) at {0}'.format(dir_path))

def handle_task(task, context):
    manage = UsbRule(task, context)
    manage.handle_task()