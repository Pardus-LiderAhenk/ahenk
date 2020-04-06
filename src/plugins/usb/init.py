#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Init(AbstractPlugin):
    def __init__(self, context):
        super(Init, self).__init__()
        self.context = context
        self.logger = self.get_logger()

        self.script = '/bin/bash ' + self.Ahenk.plugins_path() + 'usb/scripts/{0}'

        self.logger.debug('Parameters were initialized.')

    def handle_init_mode(self):
        self.execute(self.script.format('ENABLED_webcam.sh'), result=True)
        self.logger.debug('Enabled webcam.')

        self.execute(self.script.format('ENABLED_printer.sh'), result=True)
        self.logger.debug('Enabled printer.')

        self.execute(self.script.format('ENABLED_usbstorage.sh'), result=True)
        self.logger.debug('Enabled usb storage.')

        self.execute(self.script.format('ENABLED_usbhid.sh'), result=True)
        self.logger.debug('Enabled usb hid.')


def handle_mode(context):
    init = Init(context)
    init.handle_init_mode()
