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
        if self.is_installed('quota') is False:
            self.logger.debug('Installing quota with apt-get...')
            self.install_with_apt_get('quota')


def handle_mode(context):
    init = Init(context)
    init.handle_init_mode()
