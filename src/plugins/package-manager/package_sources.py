#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json
from base.plugin.abstract_plugin import AbstractPlugin
from os import listdir
from os.path import isfile, join

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
                result_code, p_out, p_err = self.execute(
                    '/bin/bash {}package-manager/scripts/sourcelist.sh'.format(self.Ahenk.plugins_path()))

                repo_not_found = True
                for line in p_out.splitlines():
                    if item == line:
                        repo_not_found = False
                        break

                if repo_not_found:
                    file_source_list = open("/etc/apt/sources.list.d/liderahenk.list", 'a+')
                    file_source_list.write(item + "\n")
                    file_source_list.close()

                if result_code != 0:
                    self.logger.error("Error occurred while adding repository: " + str(p_err))
                    error_message += " Paket deposu eklenirken hata oluştu: " + str(p_err)
            self.logger.debug("Added repositories")

            # Remove desired repositories
            for item in deleted_items:
                command = 'find /etc/apt/ -name \*.list -type f -exec sed -i \'/' + str(item).replace("/",
                                                                                                      "\\/") + '/d\' \{\} \;'
                #deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main
                is_file_deleted = False
                f_name_list = [f for f in listdir("/etc/apt/sources.list.d") if isfile(join("/etc/apt/sources.list.d", f))]
                for idx, f_name in enumerate(f_name_list):
                    f_name_list[idx] = "/etc/apt/sources.list.d/" + f_name

                f_name_list.append("/etc/apt/sources.list")
                for f_name in f_name_list:
                    file_sources = open(f_name, 'r')
                    file_data = file_sources.read()
                    file_sources.close()
                    if item in file_data:
                        file_data = file_data.replace(item, "")
                        is_file_deleted = True
                        file_sources = open(f_name, 'w')
                        file_sources.write(file_data)
                        file_sources.close()
                        break

                #result_code, p_out, p_err = self.execute(command)

                if is_file_deleted is False:
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
