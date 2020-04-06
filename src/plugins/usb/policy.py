#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class Usb(AbstractPlugin):
    def __init__(self, data, context):
        super(Usb, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.parameters = json.loads(self.data)
        self.script = '/bin/bash ' + self.Ahenk.plugins_path() + 'usb/scripts/{0}'
        self.script_path = self.Ahenk.plugins_path() + 'usb/scripts/{0}'
        self.items = []

        self.command_vendor = "grep -lw '{0}' /sys/bus/usb/devices/*/manufacturer | grep -o -P '.{{0,}}/.{{0,0}}'"
        self.command_model = "grep -lw '{0}' {1}product"
        self.command_serial = "grep -lw '{0}' {1}serial"
        self.command_authorized = "echo '{0}' > {1}authorized"

        self.command_serial_is_exist = 'if test -e {0}serial; then echo "exist"; else echo "not found"; fi'

        self.logger.debug('Parameters were initialized.')

    def handle_policy(self):
        try:
            self.logger.debug('Permissions will be applied for profile.')
            self.manage_permissions()
            if self.has_attr_json(self.parameters, 'items') is True:
                self.items = self.parameters['items']
                self.logger.debug('Blacklist/Whitelist will be created for profile.')
                if self.has_attr_json(self.parameters, 'type') is True:
                    self.logger.debug('BlackList Whitelist will be created....')
                    self.create_blacklist_whitelist()

            self.logger.info('USB profile is handled successfully.')
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value,
                                         message='USB izinleri başarıyla güncellendi.')

        except Exception as e:
            self.logger.error('A problem occurred while handling USB policy. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value,
                                         message='USB politikası uygulanırken bir hata oluştu: {0}'.format(str(e)))

    def manage_permissions(self):

        self.logger.debug('Changing permissions...')

        if self.has_attr_json(self.parameters, 'webcam') is True:
            if self.parameters['webcam'] == '1':
                self.execute(self.script.format('ENABLED_webcam.sh'), result=True)
            elif self.parameters['webcam'] == '0':
                self.execute(self.script.format('DISABLED_webcam.sh'), result=True)

            self.logger.debug('Applied permission change for parameter "webcam"')
        else:
            self.logger.debug('Data has no parameter "webcam"')

        if self.has_attr_json(self.parameters, 'printer') is True:
            if self.parameters['printer'] == '1':
                self.execute(self.script.format('ENABLED_printer.sh'), result=True)
            elif self.parameters['printer'] == '0':
                self.execute(self.script.format('DISABLED_printer.sh'), result=True)

            self.logger.debug('Applied permission change for parameter "printer"')
        else:
            self.logger.debug('Data has no parameter "printer"')

        if self.has_attr_json(self.parameters, 'storage') is True:
            if self.parameters['storage'] == '1':
                self.execute(self.script.format('ENABLED_usbstorage.sh'), result=True)
            elif self.parameters['storage'] == '0':
                self.execute(self.script.format('DISABLED_usbstorage.sh'), result=True)

            self.logger.debug('Applied permission change for parameter "storage"')
        else:
            self.logger.debug('Data has no parameter "storage"')

        if self.has_attr_json(self.parameters, 'mouseKeyboard') is True:
            if self.parameters['mouseKeyboard'] == '1':
                self.execute(self.script.format('ENABLED_usbhid.sh'), result=True)
            elif self.parameters['mouseKeyboard'] == '0':
                self.execute(self.script.format('DISABLED_usbhid.sh'), result=True)

            self.logger.debug('Applied permission change for parameter "mouseKeyboard"')
        else:
            self.logger.debug('Data has no parameter "mouseKeyboard"')

        self.logger.debug('Permissions were applied.')

    def organize_rule_files(self, is_whitelist):
        if is_whitelist == 0:
            if self.is_exist("/etc/udev/rules.d/99-whitelist.rules"):
                self.delete_file("/etc/udev/rules.d/99-whitelist.rules")
            self.execute('> /etc/udev/rules.d/99-blacklist.rules')
        else:
            if self.is_exist("/etc/udev/rules.d/99-blacklist.rules"):
                self.delete_file("/etc/udev/rules.d/99-blacklist.rules")
            self.execute('> /etc/udev/rules.d/99-whitelist.rules')

    def write_whitelist_line(self, vendor, model, serial_number, is_first_line):
        command_blackandwhitelist = 'echo ' + "'"
        symbol = '='
        authorized = '1'
        if is_first_line is True:
            command_blackandwhitelist = 'ex -sc ' + "'1i|"
            symbol = '!'
            authorized = '0'
        command_blackandwhitelist += 'ACTION==\"add|change\" , SUBSYSTEM==\"usb\" , '
        if vendor is not None and len(vendor) > 0:
            command_blackandwhitelist += ' ATTR{manufacturer}' + symbol + '=\"' + vendor + '\" , '
        if model is not None and len(model) > 0:
            command_blackandwhitelist += ' ATTR{product}' + symbol + '=\"' + model + '\" , '
        if serial_number is not None and len(serial_number) > 0:
            command_blackandwhitelist += ' ATTR{serial}' + symbol + '=\"' + serial_number + '\" , '
        command_blackandwhitelist += ' ATTR{authorized}=\"' + authorized + '\" ' + "'"
        if is_first_line is False:
            command_blackandwhitelist += ' >> '
        else:
            command_blackandwhitelist += ' -cx '
        command_blackandwhitelist += '/etc/udev/rules.d/99-whitelist.rules'
        self.logger.debug(command_blackandwhitelist)
        self.write_rule_line(command_blackandwhitelist)

    def write_rule_line(self, command):
        p_result_code, p_out, p_err = self.execute(command)
        if p_result_code == 0:
            self.logger.debug('Rule line is added successfully')
        elif p_result_code != 0:
            self.logger.debug('Error while adding rule line to /etc/udev/rules.d/ , Error message : {0}'.format(p_err))

    def create_rule_line(self, vendor, model, serial_number, is_whitelist):
        if is_whitelist == 0:
            command_blackandwhitelist = 'echo ' + "'" + 'ACTION ==\"add|change\" , SUBSYSTEM==\"usb\" , '
            if vendor is not None and len(vendor) > 0:
                command_blackandwhitelist += ' ATTR{manufacturer}==\"' + vendor + '\" , '
            if model is not None and len(model) > 0:
                command_blackandwhitelist += ' ATTR{product}==\"' + model + '\" , '
            if serial_number is not None and len(serial_number) > 0:
                command_blackandwhitelist += ' ATTR{serial}==\"' + serial_number + '\" , '
            command_blackandwhitelist += ' ATTR{authorized}=\"0\" ' + "'" + '>> /etc/udev/rules.d/99-blacklist.rules'
            self.write_rule_line(command_blackandwhitelist)
        else:
            self.write_whitelist_line(vendor, model, serial_number, True)
            self.write_whitelist_line(vendor, model, serial_number, False)

    def create_blacklist_whitelist(self):
        self.logger.debug('usb storage will be enabled')
        self.execute(self.script.format('ENABLED_usbstorage.sh'), result=True)
        self.logger.debug('usb storage enabled')
        if self.parameters['type'] == 'blacklist':
            is_whitelist = 0
        else:
            is_whitelist = 1
        self.logger.debug('Rule files are organizing....')
        self.organize_rule_files(is_whitelist)
        self.logger.debug('Rule files are organized')

        for item in self.items:
            item_parameters = json.loads(str(json.dumps(item)))
            vendor = item_parameters['vendor']
            model = item_parameters['model']
            serial_number = item_parameters['serialNumber']

            self.create_rule_line(vendor, model, serial_number, is_whitelist)

            self.logger.debug('vendor, model and serial number is set....')
            self.logger.debug(self.command_vendor.format(vendor))
            result_code, p_out, p_err = self.execute(self.command_vendor.format(vendor), result=True)
            folder_list = str(p_out).split('\n')
            folder_list.pop()

            if p_out == '' and vendor != '':
                self.logger.debug('Device has not been found because of vendor. Vendor: {0}'.format(vendor))

            if vendor == '':
                folder_list = []
                folder_list.append('/sys/bus/usb/devices/*/')

            for folder in folder_list:

                result_code, p_out, p_err = self.execute(self.command_model.format(model, folder), result=True)

                if p_out == '' and model != '':
                    self.logger.debug(
                        'Device model has not been found in this directory. Directory: {0}, Vendor: {1}, Model: {2}'.format(
                            folder, vendor, model))

                else:
                    model_folder_list = str(p_out).split('\n')
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
                            result_code, p_out, p_err = self.execute(self.command_serial_is_exist.format(model_folder),
                                                                     result=True)

                        if 'exist' in p_out or model_folder == '/sys/bus/usb/devices/*/':
                            result_code, p_out, p_err = self.execute(
                                self.command_serial.format(serial_number, model_folder),
                                result=True)
                            if p_out == '' and serial_number != '':
                                self.logger.debug(
                                    'Device serial number has not been found in this directory. Directory: {0}, Vendor: {1}, Model: {2}, Serial Number: {3}'.format(
                                        model_folder, vendor,
                                        model, serial_number))
                            else:
                                serial_folder_list = str(p_out).split('\n')
                                serial_folder_list.pop()

                                if p_out == '':
                                    serial_folder_list.append(model_folder)

                                for serial_folder in serial_folder_list:
                                    serial_folder = serial_folder.strip('serial')
                                    if self.parameters['type'] == 'whitelist':
                                        self.execute(self.command_authorized.format('1', serial_folder), result=True)
                                        self.logger.debug(
                                            'Enabled the device. Directory: {0}, Vendor: {1}, Model: {2}, Serial Number: {3}'.format(
                                                serial_folder, vendor, model, serial_number))
                                    elif self.parameters['type'] == 'blacklist':
                                        self.execute(self.command_authorized.format('0', serial_folder), result=True)
                                        self.logger.debug(
                                            'Disabled the device. Directory: {0}, Vendor: {1}, Model: {2}, Serial Number: {3}'.format(
                                                serial_folder, vendor, model, serial_number))

                        elif 'not found' in p_out:
                            dir = ''
                            if model != '':
                                dir = model_folder
                            elif vendor != '':
                                dir = folder

                            if self.parameters['type'] == 'whitelist':
                                self.execute(self.command_authorized.format('1', dir), result=True)
                                self.logger.debug(
                                    'Enabled the device. Directory: {0}, Vendor: {1}, Model: {2}, Serial Number: {3}'.format(
                                        dir, vendor, model, serial_number))
                            elif self.parameters['type'] == 'blacklist':
                                self.execute(self.command_authorized.format('0', dir), result=True)
                                self.logger.debug(
                                    'Disabled the device. Directory: {0}, Vendor: {1}, Model: {2}, Serial Number: {3}'.format(
                                        dir, vendor, model, serial_number))

        self.execute('udevadm control --reload-rules')
        self.logger.debug('Blacklist/Whitelist was created.')


def handle_policy(profile_data, context):
    manage = Usb(profile_data, context)
    manage.handle_policy()
