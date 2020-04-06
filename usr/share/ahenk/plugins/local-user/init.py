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

    def handle_mode(self):
        if self.is_installed('whois') is False:
            self.install_with_apt_get('whois')
            self.logger.debug('whois has been installed with apt-get.')


def handle_mode(context):
    init = Init(context)
    init.handle_mode()
