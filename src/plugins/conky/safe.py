#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.plugin.abstract_plugin import AbstractPlugin

class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.username = self.get_username()
        self.logger = self.get_logger()
        self.logger.debug('Parameters were initialized.')

    def handle_safe_mode(self):
        # Killing conky processes
        self.logger.debug('Conky named processes will be killed.')
        self.execute('killall -9 conky')
        # delete autostart and conky config file of logout username
        self.homedir = self.get_homedir(self.get_username()) + '/'
        self.conky_config_file_dir = '{0}.conky/'.format(self.homedir)
        self.conky_config_file_path = '{0}conky.conf'.format(self.conky_config_file_dir)
        if self.is_exist(self.conky_config_file_dir):
            self.logger.debug('Conky config file will be deleted of {0}.'.format(self.username))
            self.delete_file(self.conky_config_file_path)

        self.autostart_dir_path = '{0}.config/autostart/'
        self.autorun_file_path = '{0}conky.desktop'
        auto_start_file = self.autorun_file_path.format(self.autostart_dir_path.format(self.homedir))
        if self.is_exist(auto_start_file):
            self.delete_file(auto_start_file)
            self.logger.debug('Removing autostart file of user {0}'.format(self.username))

def handle_mode(context):
    safe = Safe(context)
    safe.handle_safe_mode()
