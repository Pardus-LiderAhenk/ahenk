#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
from base.util.apt_helper import AptHelper


class PackageArchive(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        self.logger.debug('Handling Package Archive Task')
        try:
            resultMessage = ''
            package_name = str((self.data)['packageName'])
            package_version = str((self.data)['packageVersion'])
            self.logger.debug("Installing new package... {0}".format(package_name))
            versions = {package_name: package_version} if package_version else None
            result_code, p_result, p_err = AptHelper.install_packages(
                [package_name],
                versions=versions,
                update_cache=True,
                run_dpkg_configure=True,
            )
            if result_code == 0:
                resultMessage += 'Paket başarıyla kuruldu - {0}={1}'.format(package_name, package_version)
                self.logger.debug(resultMessage)
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message=resultMessage)
            else:
                self.logger.debug(resultMessage)
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Önceki paket sürümü kurulumunda beklenmedik hata!',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.debug(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Önceki paket sürümü kurulumunda beklenmedik hata!',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)


def handle_task(task, context):
    plugin = PackageArchive(task, context)
    plugin.handle_task()
