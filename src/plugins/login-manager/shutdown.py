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
        self.logger.debug('Removing login-manager cron job...')
        self.execute('crontab -l | sed \'/{0}/d\' | crontab -'.format('login-manager/scripts/check.py'))


def handle_mode(context):
    shutdown = Shutdown(context)
    #shutdown.handle_shutdown_mode()
