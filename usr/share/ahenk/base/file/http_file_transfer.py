#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
from base.util.util import Util
from base.system.system import System
import urllib.request

from base.scope import Scope


class Http(object):
    def __init__(self, parameter_map):

        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.configuration_manager = scope.get_configuration_manager()
        try:
            self.url = parameter_map['url']
        except Exception as e:
            self.logger.error(
                'A problem occurred while parsing parameter map. Error Message: {0}'.format(str(e)))

    def send_file(self, local_path, md5):
        pass

    def get_file(self):

        self.logger.debug('[FileTransfer] Getting file ...')
        file_md5 = None
        try:
            tmp_file_name = str(Util.generate_uuid())
            local_full_path = System.Ahenk.received_dir_path() + tmp_file_name
            urllib.request.urlretrieve(self.url, local_full_path)
            file_md5 = str(Util.get_md5_file(local_full_path))
            Util.rename_file(local_full_path, System.Ahenk.received_dir_path() + file_md5)
            self.logger.debug('File was downloaded to {0} from {1}'.format(local_full_path, self.url))
        except Exception as e:
            self.logger.error(
                'A problem occurred while downloading file. Exception message: {0}'.format(str(e)))
            raise
        return file_md5

    def disconnect(self):
        pass

    def is_connected(self):
        pass

    def connect(self):
        pass
