#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Caner Feyzullahoglu <caner.feyzullahoglu@agem.com.tr>
"""
Style Guide is PEP-8
https://www.python.org/dev/peps/pep-0008/
"""

from base.plugin.abstract_plugin import AbstractPlugin

class GetFile(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()

        self.logger = self.get_logger()
        self.logger.debug('Initialized')

        self.task = task
        self.context = context
        self.message_code = self.get_message_code()

    def handle_task(self):
        parameter_map = self.task
        self.logger.debug('Handling task')
        self.logger.debug('Fetching file from: {0} to {1}'.format(parameter_map['remotePath'],
                                                                  parameter_map['localPath']))

        try:
            self.context.fetch_file(parameter_map['remotePath'], local_path=parameter_map['localPath'],
                                    file_name=parameter_map['fileName'])

            for param in parameter_map:
                if param == 'editUserPermissions':
                    permissions = ''
                    if parameter_map['editUserPermissions']:
                        permissions += 'u+r' if parameter_map['readUser'] else 'u-r'
                        permissions += '+w' if parameter_map['writeUser'] else '-w'
                        permissions += '+x' if parameter_map['executeUser'] else '-x'
                        if parameter_map['ownerUser']:
                            chown_command = 'chown ' + parameter_map['ownerUser'] + ': "' + parameter_map['localPath'] \
                                            + parameter_map['fileName'] + '"'
                            self.logger.debug('Executing chown: ' + chown_command)
                            result_code, p_out, p_err = self.execute(chown_command)
                            if result_code != 0:
                                self.logger.error('Error occurred while executing chown command')
                                self.logger.error('Error message: {0}'.format(str(p_err)))
                                warning_message = 'Dosyanın sahibi değiştirilemedi, ' \
                                                  + parameter_map[
                                                      'ownerUser'] + ' kullanıcısının varolduğundan emin olun. '
                                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                             message=warning_message)
                                return
                            else:
                                if permissions:
                                    self.execute_command(permissions, parameter_map)

                elif param == 'editGroupPermissions':
                    permissions = ''
                    if parameter_map['editGroupPermissions']:
                        permissions += 'g+r' if parameter_map['readGroup'] else 'g-r'
                        permissions += '+w' if parameter_map['writeGroup'] else '-w'
                        permissions += '+x' if parameter_map['executeGroup'] else '-x'
                        if parameter_map['ownerGroup']:
                            chown_command = 'chown ' + ':' + parameter_map['ownerGroup'] + ' "' \
                                            + parameter_map['localPath'] \
                                            + parameter_map['fileName'] + '"'
                            self.logger.debug('Executing chown: ' + chown_command)
                            result_code, p_out, p_err = self.execute(chown_command)
                            if result_code != 0:
                                self.logger.error('Error occurred while executing chown command')
                                self.logger.error('Error message: {0}'.format(str(p_err)))
                                warning_message = 'Dosyanın sahibi değiştirilemedi, ' \
                                                  + parameter_map['ownerGroup'] + ' grubunun varolduğundan emin olun. '
                                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                             message=warning_message)
                                return
                            else:
                                if permissions:
                                    self.execute_command(permissions, parameter_map)

                elif param == 'editOtherPermissions':
                    permissions = ''
                    if parameter_map['editOtherPermissions']:
                        permissions += 'o+r' if parameter_map['readOther'] else 'o-r'
                        permissions += '+w' if parameter_map['writeOther'] else '-w'
                        permissions += '+x' if parameter_map['executeOther'] else '-x'
                    if permissions:
                        self.execute_command(permissions, parameter_map)

                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Dosya transferi başarıyla gerçekleştirildi')

        except Exception as e:
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='NETWORK INVENTORY Dosya transferi gerçekleştirilirken hata oluştu: ' + str(e))

    def execute_command(self, permissions, parameter_map):
        chmod_command = 'chmod ' + permissions + ' "' + parameter_map['localPath'] \
                        + parameter_map['fileName'] + '"'
        self.logger.debug('Executing chmod: ' + chmod_command)
        result_code, p_out, p_err = self.execute(chmod_command)
        if result_code != 0:
            self.logger.error('Error occurred while executing chmod command')
            self.logger.error('Error message: {0}'.format(str(p_err)))
            warning_message = 'Dosyanın hakları değiştirilirken hata oluştu.'
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message=warning_message)
            return
        else:
            self.logger.info('Dosya hakları başarılıyla düzenlendi.')
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message="Dosya hakları başarılıyla düzenlendi")


def handle_task(task, context):
    scan = GetFile(task, context)
    scan.handle_task()
