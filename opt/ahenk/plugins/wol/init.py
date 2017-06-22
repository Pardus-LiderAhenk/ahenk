#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Init(AbstractPlugin):
    def __init__(self, context):
        super(Init, self).__init__()
        self.context = context
        self.logger = self.get_logger()

        self.logger.debug('Parameters were initialized.')

    def handle_init_mode(self):

        if self.is_installed('wakeonlan') is False:
            self.logger.debug('Installing wakeonlan with apt-get...')
            self.install_with_apt_get('wakeonlan')

        for interface in self.Hardware.Network.interfaces():
            self.logger.debug('Activating magic packet for ' + str(interface))
            self.execute('ethtool -s ' + str(interface) + ' wol g')
            self.logger.debug('Activated magic packet for ' + str(interface))


def handle_mode(context):
    init = Init(context)
    init.handle_init_mode()
