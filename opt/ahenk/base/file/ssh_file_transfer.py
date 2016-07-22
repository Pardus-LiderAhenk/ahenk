#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.util.util import Util
from base.system.system import System
from base.Scope import Scope
import paramiko
import logging


class Ssh(object):
    def __init__(self, parameter_map):

        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()
        logging.getLogger("paramiko").setLevel(logging.INFO)

        try:
            self.target_hostname = parameter_map['host']
            self.target_port = parameter_map['port']
            self.target_username = parameter_map['username']
            self.target_path = parameter_map['path']
            self.target_password = None
            self.p_key = None
            if Util.has_attr_json(parameter_map, 'password'):
                self.target_password = parameter_map['password']
            else:
                self.p_key = parameter_map['pkey']
        except Exception as e:
            self.logger.error('[Ssh] A problem occurred while parsing ssh connection parameters. Error Message: {}'.format(str(e)))

        self.connection = None
        self.logger.debug('[Ssh] Parameters set up')

    def send_file(self, local_path, md5):

        self.logger.debug('[Ssh]  {0} is sending to  {1}'.format(local_path, self.target_path + md5))
        try:
            sftp = paramiko.SFTPClient.from_transport(self.connection)
            try:
                sftp.chdir(self.target_path)  # Test if remote_path exists
            except IOError:
                sftp.mkdir(self.target_path)  # Create remote_path
                sftp.chdir(self.target_path)

            sftp.put(local_path, self.target_path + md5)
            self.logger.debug('[Ssh] File was sent to {0} from {1}'.format(local_path, self.target_path))
            return True
        except Exception as e:
            self.logger.error('[Ssh] A problem occurred while sending file. Exception message: {}'.format(str(e)))
            return False

    def get_file(self):
        self.logger.debug('[Ssh] Getting file ...')
        file_md5 = None
        try:
            tmp_file_name = str(Util.generate_uuid())
            local_full_path = System.Ahenk.received_dir_path() + tmp_file_name
            sftp = paramiko.SFTPClient.from_transport(self.connection)
            sftp.get(self.target_path, local_full_path)
            file_md5 = str(Util.get_md5_file(local_full_path))
            Util.rename_file(local_full_path, System.Ahenk.received_dir_path() + file_md5)
            self.logger.debug('[Ssh] File was downloaded to {0} from {1}'.format(local_full_path, self.target_path))
        except Exception as e:
            self.logger.error('[Ssh] A problem occurred while downloading file. Exception message: {}'.format(str(e)))
            raise
        return file_md5

    def connect(self):
        self.logger.debug('[FileTransfer]  Connecting to {} via {}'.format(self.target_hostname, self.target_port))
        try:
            connection = paramiko.Transport(self.target_hostname, int(self.target_port))
            connection.connect(username=self.target_username, password=self.target_password, pkey=self.p_key)
            self.connection = connection
            self.logger.debug('[FileTransfer] Connected.')
        except Exception as e:
            self.logger.error('[FileTransfer] A problem occurred while connecting to {} . Exception message: {}'.format(self.target_hostname, str(e)))

    def disconnect(self):
        self.connection.close()
        self.logger.debug('[FileTransfer] Connection is closed.')
        # TODO
        pass

    def is_connected(self):
        # TODO
        pass
