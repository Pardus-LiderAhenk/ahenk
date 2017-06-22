#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Shutdown(AbstractPlugin):
    def __init__(self, context):
        super(Shutdown, self).__init__()
        self.context = context
        self.logger = self.get_logger()

        self.logger.debug('Parameters were initialized.')

    def handle_shutdown_mode(self):
        for interface in self.Hardware.Network.interfaces():
            self.logger.debug('Activating magic packet for ' + str(interface))
            self.execute('ethtool -s ' + str(interface) + ' wol g')
            self.logger.debug('Activated magic packet for ' + str(interface))


def handle_mode(context):
    shutdown = Shutdown(context)
    shutdown.handle_shutdown_mode()
