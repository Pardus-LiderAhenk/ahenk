#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.plugin.abstract_plugin import AbstractPlugin


class Init(AbstractPlugin):
    def __init__(self, context):
        super(Init, self).__init__()
        self.context = context
        self.logger = self.get_logger()

    def handle_mode(self):
        try:
            if self.is_installed('chkconfig') is False:
                result_code, result, error = self.install_with_apt_get('chkconfig')
                if result_code != 0:
                    self.logger.error('Package chkconfig can not be installed')
                else:
                    self.logger.debug("[PACKAGE MANAGER -INIT] Package chkconfig installed successfully")
            if self.is_installed('acct') is False:
                result_code, result, error = self.install_with_apt_get('acct')
                if result_code != 0:
                    self.logger.error("Package acct can not be installed")
                else:
                    self.logger.debug("Package acct installed successfully")
        except Exception as e:
            self.logger.error('Error while installing chkconfig and acct packages. Error message : {0}'.format(str(e)))
        result_code, result, error = self.execute('chkconfig acct on')
        try:
            if result_code == 0:
                result_code, result, error = self.execute('/etc/init.d/acct start')
                if result_code == 0:
                    self.logger.debug('acct service started successfully')
                else:
                    self.logger.error(
                        'acct service could not be started - Error while executing /etc/init.d/acct start command')
            else:
                self.logger.error('chkconfig acct on command could not executed')
        except Exception as e:
            self.logger.error('Error while starting acct service. Error message : {0}'.format(str(e)))


def handle_mode(context):
    init = Init(context)
    init.handle_mode()
