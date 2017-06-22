#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import os
from glob import glob

from base.plugin.abstract_plugin import AbstractPlugin


class Packages(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        self.logger.debug('Handling Packages Task')
        try:
            cn = '{0}\r\n'.format(self.Ahenk.dn().split(',')[0])

            items = (self.data)['packageInfoList']
            for item in items:
                try:
                    if self.has_attr_json(item, 'tag') and self.has_attr_json(item, 'source'):
                        array = item['source'].split()
                        source = ' '
                        source = source.join(array)

                        ## REPO ADD / CHECK

                        self.logger.debug(
                            "Checking source {0}".format(item['source']))

                        if self.is_repo_exist(source):
                            self.logger.debug('{0} Source already exists'.format(source))
                        else:
                            self.logger.debug('Source adding...')
                            try:
                                self.add_source(source)
                            except Exception as e:
                                self.logger.error('Source could not added')
                                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                             message='{0}\n Kaynaklar eklenmeye çalışırken hata oluştu. Hata Mesajı:{1}'.format(
                                                                 cn, str(e)))
                                return

                            self.logger.debug('{0} Source added'.format(source))

                            return_code_update, result_update, error_update = self.execute('apt-get update')
                            if return_code_update == 0:
                                self.logger.debug('Packages were updated')
                            else:
                                self.logger.error('Packages could not updated')
                                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                             message='{0}\n Kaynaklar güncellenmeye çalışırken hata oluştu. Hata Mesajı: {1}'.format(
                                                                 cn, str(error_update)))
                                return

                        ## INSTALL/REMOVE PACKAGE

                        if item['tag'] == 'Yükle' or item['tag'] == 'Install':
                            self.logger.debug(
                                "Installing new package... {0}".format(item['packageName']))
                            result_code, p_result, p_err = self.install_with_apt_get(item['packageName'],
                                                                                     item['version'])
                            if result_code == 0:
                                self.logger.debug(
                                    "Package installed : {0}={1}".format(item['packageName'],
                                                                         item['version']))
                            else:
                                self.logger.error(
                                    "Package could not be installed : {0}={1} "
                                    ". Error Message:{2}".format(
                                        item['packageName'], item['version'], str(p_err)))
                                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                             message='{0}\n Source eklendi fakat paket kurulurken '
                                                                     'hata oluştu. Hata Mesajı: {1}'.format(
                                                                 cn, str(p_err)))
                                return
                        elif item['tag'] == 'Kaldır' or item['tag'] == 'Uninstall':
                            result_code, p_result, p_err = self.uninstall_package(item['packageName'],
                                                                                  item['version'])

                            if result_code == 0:
                                self.logger.debug(
                                    "Package installed : {0}={1}".format(item['packageName'],
                                                                         item['version']))
                            else:
                                self.logger.error(
                                    "Package could not be installed : {0}={1}".format(
                                        item['packageName'],
                                        item['version']))
                                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                             message='{0}\n Paket kaldırılırken '
                                                                     'hata oluştu. Hata Mesajı: {1}'.format(
                                                                 cn, str(p_err)))
                except Exception as e:
                    self.logger.error('Unpredictable error exists. Error Message: {0}'.format(str(e)))
                    self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                 message='{0}.\nÖngörülemeyen bir hata oluştu.Hata mesajı:{1}'.format(
                                                     cn, str(e)))
                    return

            self.logger.debug('Task handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='{0}\nTüm paket işlemleri başarıyla çalıştırıldı'.format(cn))
        except Exception as e:
            self.logger.error('Unpredictable error exists. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='{0}\nGörev çalıştırılırken beklenmedik bir hata oluştu. Hata Mesajı: {1}'.format(
                                             cn,
                                             str(e)))

    def is_repo_exist(self, source):
        if source in open('/etc/apt/sources.list').read():
            return True

        for f_list_path in glob('/etc/apt/sources.list.d/*'):
            if os.path.isfile(f_list_path):
                if source in open(f_list_path).read():
                    return True
        return False

    def add_source(self, source):
        self.write_file('/etc/apt/sources.list.d/ahenk.list', source, 'a+')


def handle_task(task, context):
    plugin = Packages(task, context)
    plugin.handle_task()
