#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.scope import Scope
from base.file.ssh_file_transfer import Ssh
from base.file.http_file_transfer import Http


class FileTransferManager(object):
    def __init__(self, protocol, parameter_map):
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()
        self.transporter = self.get_instance(protocol, parameter_map)

    def get_instance(self, protocol, parameter_map):
        try:
            transporter = None
            if str(protocol).lower() == 'ssh':
                transporter = Ssh(parameter_map)
            elif str(protocol).lower() == 'http':
                transporter = Http(parameter_map)
            else:
                raise Exception('Unsupported file transfer protocol: {0}'.format(str(protocol)))
            return transporter

        except Exception as e:
            self.logger.error(
                '[FileTransferManager] A problem occurred while getting instance of related protocol. Error Message: {0}'.format(
                    str(e)))
            return None
