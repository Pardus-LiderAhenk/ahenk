#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.Scope import Scope
import paramiko


class FileTransfer(object):
    def __init__(self, hostname, port, username, password, pkey=None):

        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()

        self.target_hostname = hostname
        self.port = port
        self.target_username = username
        self.target_password = password
        self.p_key = pkey
        self.connection = None

        self.logger.debug('[FileTransfer] Parameters set up')

    def send_file(self, local_path, remote_path):
        self.logger.debug('[FileTransfer]  Sending file ...')

        try:
            sftp = paramiko.SFTPClient.from_transport(self.connection)
            sftp.put(local_path, remote_path)
            self.logger.debug('[FileTransfer] File was sent to {} from {}'.format(local_path, remote_path))
        except Exception as e:
            self.logger.error('[FileTransfer] A problem occurred while sending file. Exception message: {}'.format(str(e)))
        finally:
            self.connection.close()
            self.logger.debug('[FileTransfer] Connection is closed successfully')

    def get_file(self, local_path, remote_path):
        self.logger.debug('[FileTransfer] Getting file ...')
        try:
            sftp = paramiko.SFTPClient.from_transport(self.connection)
            sftp.get(remote_path, local_path)
            self.logger.debug('[FileTransfer] File was downloaded to {} from {}'.format(local_path, remote_path))
        except Exception as e:
            self.logger.error('[FileTransfer] A problem occurred while downloading file. Exception message: {}'.format(str(e)))
        finally:
            self.connection.close()
            self.logger.debug('[FileTransfer] Connection is closed successfully')

    def connect(self):
        self.logger.debug('[FileTransfer]  Connecting to {} via {}'.format(self.target_hostname, self.port))
        try:
            connection = paramiko.Transport((self.target_hostname, int(self.port)))
            connection.connect(username=self.target_username, password=self.target_password, pkey=self.p_key)
            self.connection = connection
            self.logger.debug('[FileTransfer] Connected.')
        except Exception as e:
            self.logger.error('[FileTransfer] A problem occurred while connecting to {} . Exception message: {}'.format(self.target_hostname, str(e)))
