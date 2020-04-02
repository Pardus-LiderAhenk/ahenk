#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from base.plugin.abstract_plugin import AbstractPlugin


class Init(AbstractPlugin):
    def __init__(self, context):
        super(Init, self).__init__()
        self.context = context
        self.logger = self.get_logger()
        self.plugin_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.initial_rules_file_path = self.plugin_path + '/iptables.rules'
        self.logger.debug('[FIREWALL - init] Parameters were initialized.')

    def handle_mode(self):

        if self.is_installed('iptables-persistent') is False:
            self.install_with_apt_get('iptables-persistent')
        pass

        try:
            if self.is_exist(self.initial_rules_file_path):
                self.logger.debug('[FIREWALL - init] Adding initial rules temp file to iptables-restore as parameter...')
                self.execute('/sbin/iptables-restore < {}'.format(self.initial_rules_file_path))

                self.logger.debug('[FIREWALL - init] Save the rules...')
                self.execute('service netfilter-persistent save')

                self.logger.debug('[FIREWALL - init] Restart the service...')
                self.execute('service netfilter-persistent restart')

        except Exception as e:
            self.logger.error('[FIREWALL - init] A problem occured while handling Firewall init.py: {0}'.format(str(e)))


def handle_mode(context):
    init = Init(context)
    init.handle_mode()
