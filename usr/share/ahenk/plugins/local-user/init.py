#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
from base.util.apt_helper import AptHelper


class Init(AbstractPlugin):
    def __init__(self, context):
        super(Init, self).__init__()
        self.context = context
        self.logger = self.get_logger()

        self.logger.debug('Parameters were initialized.')

    def handle_mode(self):
        if self.is_installed('whois') is False:
            AptHelper.install_packages(['whois'], update_cache=True, run_dpkg_configure=True)
            self.logger.debug('whois has been installed with apt.')


def handle_mode(context):
    init = Init(context)
    init.handle_mode()
