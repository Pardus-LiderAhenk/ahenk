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
            
            result_message = "Paket yüklü"
            if dn is None:
                dn = " "
            res["package_name"] = package_name
            res["dn"] = dn
            result_code, result, p_err = self.execute('dpkg -s {} | grep Version'.format(package_name))
            data = result.split(': ')
            if data:
                if data[0] == 'Version' :  # Package is installed
                    if package_version is None or len(package_version) == 0:
                        self.logger.debug(package_version)
                        result = 1
                        result_message = "Paket yüklü"
                        res['version'] = data[1]
                        res["res"] = result      
                    elif package_version is not None and str((package_version + '\n')) == str(data[1]):  # Package version is the same with wanted version
                        result = 1
                        result_message = "Paket yüklü"
                        res['version'] = data[1]
                        res["res"] = result      
                    else:
                        self.logger.debug(package_version)
                        result = 2
                        result_message = "Paket farklı veriyonla yüklü"
                        res['version'] = data[1]
                        res["res"] = result      
                else:  # Package is not installed
                    result = 0
                    result_message = "Paket yüklü değil"
                    res['version'] = ''
                    res["res"] = result      

                self.logger.debug("Result is: - {}".format(result_message))
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                            message='{0} - {1}'.format(package_name, result_message),
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
