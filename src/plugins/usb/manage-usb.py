#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class ManageUsb(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        if self.has_attr_json(task, 'webcam') is True:
            self.webcam = self.task['webcam']

        if self.has_attr_json(task, 'mouseKeyboard') is True:
            self.mouse_keyboard = self.task['mouseKeyboard']

        if self.has_attr_json(task, 'printer') is True:
            self.printer = self.task['printer']

        if self.has_attr_json(task, 'storage') is True:
            self.storage = self.task['storage']

        self.script = '/bin/bash ' + self.Ahenk.plugins_path() + 'usb/scripts/{0}'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            self.logger.debug('Changing permissions...')

            if self.has_attr_json(self.task, 'webcam') is True:
                if self.webcam == '1':
                    self.execute(self.script.format('ENABLED_webcam.sh'), result=True)
                elif self.webcam == '0':
                    self.execute(self.script.format('DISABLED_webcam.sh'), result=True)

                self.logger.debug('Applied permission change for parameter "webcam"')
            else:
                self.logger.debug('Task has no parameter "webcam"')

            if self.has_attr_json(self.task, 'printer') is True:
                if self.printer == '1':
                    self.execute(self.script.format('ENABLED_printer.sh'), result=True)
                elif self.printer == '0':
                    self.execute(self.script.format('DISABLED_printer.sh'), result=True)

                self.logger.debug('Applied permission change for parameter "printer"')
            else:
                self.logger.debug('Task has no parameter "printer"')

            if self.has_attr_json(self.task, 'storage') is True:
                if self.storage == '1':
                    self.execute(self.script.format('ENABLED_usbstorage.sh'), result=True)
                elif self.storage == '0':
                    self.execute(self.script.format('DISABLED_usbstorage.sh'), result=True)

                self.logger.debug('Applied permission change for parameter "storage"')
            else:
                self.logger.debug('Task has no parameter "storage"')

            if self.has_attr_json(self.task, 'mouseKeyboard') is True:
                if self.mouse_keyboard == '1':
                    self.execute(self.script.format('ENABLED_usbhid.sh'), result=True)
                elif self.mouse_keyboard == '0':
                    self.execute(self.script.format('DISABLED_usbhid.sh'), result=True)

                self.logger.debug('Applied permission change for parameter "mouseKeyboard"')
            else:
                self.logger.debug('Task has no parameter "mouseKeyboard"')

            self.logger.debug('Applied permission changes.')

            self.logger.info('USB task is handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='USB izinleri başarıyla güncellendi.')

        except Exception as e:
            self.logger.error('A problem occured while handling USB task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='USB izinleri güncellenirken bir hata oluştu.')


def handle_task(task, context):
    manage = ManageUsb(task, context)
    manage.handle_task()
