#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import glob
import subprocess
from base.plugin.abstract_plugin import AbstractPlugin

class Logout(AbstractPlugin):
    def __init__(self, context):
        super(Logout, self).__init__()
        self.context = context
        self.logger = self.get_logger()
        self.logger.debug('Logout process initialized.')

        self.rules_to_delete = [
            "/etc/udev/rules.d/99-whitelist.rules",
            "/etc/udev/rules.d/99-blacklist.rules",
            "/etc/udev/rules.d/99-block-webcam.rules",
            "/etc/udev/rules.d/99-block-printer.rules",
            "/etc/udev/rules.d/99-block-storage.rules",
            "/etc/udev/rules.d/99-block-hid.rules"
        ]

    def wake_up_usb_devices(self):
        try:
            devices = glob.glob('/sys/bus/usb/devices/*')
            for dev_path in devices:
                auth_file = os.path.join(dev_path, 'authorized')
                if os.path.exists(auth_file):
                    try:
                        with open(auth_file, 'r') as f:
                            status = f.read().strip()
                        if status == '0':
                            self.logger.debug(f'Waking up device: {dev_path}')
                            with open(auth_file, 'w') as f:
                                f.write('1')
                    except Exception as e:
                        self.logger.error(f'Failed to wake up device {dev_path}: {str(e)}')
        except Exception as e:
            self.logger.error(f'Error while waking up devices: {str(e)}')

    def handle_logout_mode(self):
        try:
            self.logger.debug('Cleaning up USB policies...')
            for rule_file in self.rules_to_delete:
                if self.is_exist(rule_file):
                    self.delete_file(rule_file)
                    self.logger.debug(f'Deleted: {rule_file}')
            subprocess.run(['udevadm', 'control', '--reload-rules'], check=False)
            self.wake_up_usb_devices()
            subprocess.run(['udevadm', 'trigger', '--subsystem-match=usb', '--action=add'], check=False)
            self.logger.info('USB policies cleaned up and devices woken up successfully.')

        except Exception as e:
            self.logger.error(f'Error during logout cleanup: {str(e)}')

def handle_mode(context):
    logout = Logout(context)
    logout.handle_logout_mode()