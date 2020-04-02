#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class InstalledPackages(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.temp_file_name = str(self.generate_uuid())
        self.file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)

    def handle_task(self):
        try:
            self.logger.debug('Executing command for package list.')
            self.execute(
                'dpkg-query -f=\'${{Status}},${{binary:Package}},${{Version}}\n\' -W \'*\' | grep \'install ok installed\' | sed \'s/install ok installed/i/\' | sed \'s/unknown ok not-installed/u/\' | sed \'s/deinstall ok config-files/u/\' | grep -v ahenk > {0}'.format(
                    self.file_path))
            self.logger.debug('Command executed.')

            if self.is_exist(self.file_path):
                data = {}
                md5sum = self.get_md5_file(str(self.file_path))
                self.logger.debug('{0} renaming to {1}'.format(self.temp_file_name, md5sum))
                self.rename_file(self.file_path, self.Ahenk.received_dir_path() + '/' + md5sum)
                self.logger.debug('Renamed.')
                data['md5'] = md5sum
                json_data = json.dumps(data)
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Paket listesi başarıyla okundu.',
                                             data=json_data, content_type=self.get_content_type().TEXT_PLAIN.value)
                self.logger.debug('Package list created successfully')
            else:
                raise Exception('File not found on this path: {}'.format(self.file_path))

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Paket listesi oluşturulurken hata oluştu: ' + str(e),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)


def handle_task(task, context):
    plugin = InstalledPackages(task, context)
    plugin.handle_task()
