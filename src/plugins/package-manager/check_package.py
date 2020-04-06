#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class CheckPackage(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            package_name = str((self.data)['packageName'])
            package_version = str((self.data)['packageVersion'])
            dn = self.Ahenk.dn()
            res = {}
            if dn is None:
                dn = " "
            result_code, result, p_err = self.execute('dpkg -s {} | grep Version'.format(package_name))
            data = result.split(': ')
            self.logger.debug(data)

            if data[0] == 'Version':  # Package is installed
                if package_version is None or len(package_version) == 0:
                    result = 'Paket yüklü'
                    res['version'] = data[1]
                elif data[1] is not None and (package_version + '\n') in data[
                    1]:  # Package version is the same with wanted version
                    result = 'Paket yüklü'
                    res['version'] = data[1]
                else:
                    result = 'Paket yüklü; fakat başka bir versiyonla'
                    res['version'] = data[1]
            else:  # Package is not installed
                result = 'Paket yüklü değil'
                res['version'] = ''

            res["dn"] = dn
            res["res"] = result

            self.logger.debug("Result is: - {}".format(result))
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='{0} - {1}'.format(package_name, result),
                                         data=json.dumps(res),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
            self.logger.debug("Package Info has sent")
        except Exception as e:
            self.logger.debug(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Paket Bilgilerini transferde beklenmedik hata!',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)


def handle_task(task, context):
    plugin = CheckPackage(task, context)
    plugin.handle_task()
