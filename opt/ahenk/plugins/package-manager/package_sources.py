#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class PackageSources(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        added_items = self.data['addedItems']
        deleted_items = self.data['deletedItems']
        error_message = ""
        try:
            # Add desired repositories
            for item in added_items:
                command = '(find /etc/apt/ -name \*.list -type f | xargs grep -q \'' + str(
                    item) + '\') || echo \'' + str(item) + '\' >> /etc/apt/sources.list.d/liderahenk.list'
                result_code, p_out, p_err = self.execute(command)
                if result_code != 0:
                    self.logger.error("Error occurred while adding repository: " + str(p_err))
                    error_message += " Paket deposu eklenirken hata oluştu: " + str(p_err)
            self.logger.debug("Added repositories")

            # Remove desired repositories
            for item in deleted_items:
                command = 'find /etc/apt/ -name \*.list -type f -exec sed -i \'/' + str(item).replace("/",
                                                                                                      "\\/") + '/d\' \{\} \;'
                result_code, p_out, p_err = self.execute(command)

                if result_code != 0:
                    self.logger.error("Error occurred while removing repository: " + str(p_err))
                    error_message += " Paket deposu silinirken hata oluştu: " + str(p_err)
            self.logger.debug("Removed repositories")

            # Update package lists
            self.execute('apt-get update')
            self.logger.debug("Updated package lists")

            # Read package repositories
            command = '/bin/bash {0}package-manager/scripts/sourcelist.sh'.format(self.Ahenk.plugins_path())
            result_code, p_out, p_err = self.execute(command)
            data = {}

            if result_code != 0:
                self.logger.error("Error occurred while listing repositories: " + str(p_err))
                error_message += " Paket depoları okunurken hata oluştu: " + str(p_err)
            else:
                data['packageSource'] = p_out
                self.logger.debug("Repositories are listed")

            if not error_message:
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Paket depoları başarıyla güncellendi.',
                                             data=json.dumps(data),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message=error_message,
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.debug(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message="Paket depoları güncellenirken hata oluştu: " + str(e),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)


def handle_task(task, context):
    plugin = PackageSources(task, context)
    plugin.handle_task()
