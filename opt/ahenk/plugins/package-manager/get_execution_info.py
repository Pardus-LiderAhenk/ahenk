#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class GetExecutionInfo(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.command_execution_statistic_list = []
        self.version_list = []
        self.result_message = ''
        self.commands = []
        self.logger.debug('Execution info initialized')
        self.temp_file_name = str(self.generate_uuid())
        self.file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)
        self.isRecordExist = 1

    def handle_task(self):

        self.logger.debug('Task handling')
        try:
            result_record_number = None
            commands = self.data['command']
            user = self.data['user']
            is_strict_match = self.data['isStrictMatch']
            self.create_file(self.file_path)
            # if commands fields is not empty
            if commands:
                if is_strict_match is False:
                    lastcomm_command = 'lastcomm '
                    for command in commands.split():
                        lastcomm_command += ' --command {0} '.format(command)
                    if user:
                        lastcomm_command += " --user {}".format(user)
                    self.logger.debug(
                        ' {0} command will be executed'.format(lastcomm_command))
                    result_code, result, error = self.execute(lastcomm_command + ' > /tmp/result.txt')
                    self.logger.debug(
                        ' {0} command is executed'.format(lastcomm_command))
                    result_record_number = self.check_output(result_code)
                else:
                    for command in commands.split():
                        self.logger.debug(command)
                        lastcomm_command = 'lastcomm --command {0} '.format(command)
                        if user:
                            lastcomm_command += " --user {}".format(user)
                        lastcomm_command += " --strict-match"
                        self.logger.debug(' {0} command will be executed'.format(
                            lastcomm_command))
                        result_code, result, error = self.execute(lastcomm_command + ' > /tmp/result.txt')
                        self.logger.debug(
                            ' {0} command is executed'.format(lastcomm_command))
                        result_record_number = self.check_output(result_code)
            # if command does not exist and user is exist
            elif user:
                lastcomm_command = 'lastcomm --user {0} '.format(user)
                if is_strict_match is True:
                    lastcomm_command += ' --strict-match'
                self.logger.debug(
                    ' {0} command will be executed'.format(lastcomm_command))
                result_code, result, error = self.execute(lastcomm_command + ' > /tmp/result.txt')
                self.logger.debug(
                    ' {0} command is executed + result_code = {1}'.format(
                        lastcomm_command, result_code) + ' > /tmp/result.txt')
                result_record_number = self.check_output(result_code)

            # Record not found
            if result_record_number is None:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='İstenilene uygun veri bulunamadı')
            elif self.is_exist(self.file_path):
                self.execute("sed -i '$ d' " + self.file_path)
                self.execute('echo "]," >> ' + self.file_path)
                self.execute('echo \\"versionList\\" :[ >> ' + self.file_path)
                for command_name in self.commands:
                    self.check_version_list(command_name)
                self.execute('echo "]" >> ' + self.file_path)
                self.execute('echo "}" >> ' + self.file_path)
                data = {}
                md5sum = self.get_md5_file(str(self.file_path))
                self.logger.debug('{0} renaming to {1}'.format(self.temp_file_name, md5sum))
                self.rename_file(self.file_path, self.Ahenk.received_dir_path() + '/' + md5sum)
                self.logger.debug('Renamed.')
                data['md5'] = md5sum
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Uygulama çalıştırma bilgileri başarıyla sisteme geçirildi.',
                                             data=json.dumps(data),
                                             content_type=self.get_content_type().TEXT_PLAIN.value)
                self.logger.debug("Execution Info fetched succesfully. ")
                self.logger.debug("Execution Info has sent")
            else:
                raise Exception('File not found on this path: {}'.format(self.file_path))

        except Exception as e:
            self.logger.debug(
                ' Unexpected error in get_execution.py. Error message : {0}'.format(
                    str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Uygulama çalıştırma bilgilerini getirirken beklenmedik hata!')

    def check_version_list(self, command):
        is_exist = False
        for version in self.version_list:
            if version.commandName == command:
                is_exist = True
        if not is_exist:
            result_code, result, p_err = self.execute('whereis {0}'.format(command))
            if result_code == 0 and "komut yok" not in result and len(result.split(':')) >= 2 and result[
                        len(result) - 2] != ':':
                self.logger.debug('SON HARF' + str(result[len(result) - 2]))
                result = result.split(':')[1]
                if result.split() is None or len(result.split()) == 0:
                    self.logger.debug(' Command installed place is not found')
                    self.result_message += 'Command {0} could not found'.format(command)
                else:
                    if len(self.version_list) > 0:
                        self.execute('echo , >> ' + self.file_path)
                    self.logger.debug(' Command installed place is found')

                    self.logger.debug(' Result = {0}'.format(str(result)))
                    result = result.split()
                    self.logger.debug(' Result split= {0}'.format(str(result)))
                    result = result[0]
                    self.logger.debug(
                        ' Result split 0 = {0}'.format(str(result)))

                    result_code, result, p_err = self.execute('dpkg-query -S {0}'.format(result))
                    if result_code == 0:  # Command exists
                        self.logger.debug(
                            ' Command related package name is found')
                        result = result.split(': ')[0]
                        result_code, p_result, p_err = self.execute('dpkg -s {0} | grep Version'.format(result))
                        if result_code == 0:
                            res = p_result.splitlines()
                            self.logger.debug(
                                ' Command related package version is found')
                            t_command = 'echo "{ \\"c\\": \\"' + command + '\\", \\"p\\": \\"' + result + '\\", \\"v\\":\\"' + \
                                        res[0].split(': ')[1] + '\\"}" >> ' + self.file_path
                            self.logger.debug(
                                ' Command is : {0}'.format(t_command))
                            self.execute(t_command)
                            self.logger.debug(
                                ' Appending to version list')
                            self.version_list.append(VersionInfoItem(command, result, res[0].split(': ')[1]))
                        else:
                            self.logger.debug(
                                ' Command related package version is not found')
                            self.result_message += 'Command\'s related package version could not be parsed(Deb : {0}).'.format(
                                result)
                            t_command = 'echo "{ \\"c\\": \\"' + command + '\\", \\"p\\": \\"' + result + '\\", \\"v\\":\\" - \\"}" >> ' + self.file_path
                            self.logger.debug(
                                ' Command is : {0}'.format(t_command))
                            self.execute(t_command)
                            self.logger.debug(
                                ' Appending to version list')
                            self.version_list.append(VersionInfoItem(command, result, '-'))
                    else:  # command not exists
                        self.logger.debug(
                            ' Command related package name is not found')
                        self.result_message += 'Command\'s related package could not be found(Command : {0})'.format(
                            result)
                        t_command = 'echo "{ \\"c\\": \\"' + command + '\\", \\"p\\": \\" - \\", \\"v\\":\\" - \\"}" >> ' + self.file_path
                        self.logger.debug(
                            ' Command is : {0}'.format(t_command))
                        self.execute(t_command)
                        self.logger.debug(
                            ' Appending to version list')
                        self.version_list.append(VersionInfoItem(command, '-', '-'))
            else:  # command not exists
                self.logger.debug(' Command installed place is not found')
                self.result_message += 'Command {0} could not found'.format(command)

    def check_output(self, result_code):
        try:
            if result_code == 0:
                self.logger.debug(
                    ' lastcomm execution has returned with no error')
                f = open("/tmp/result.txt", "r")
                lines = f.readlines()
                i = 0
                for line in lines:
                    if self.isRecordExist == 1:
                        self.execute('echo { \\"commandExecutionInfoList\\" :[ >> ' + self.file_path)
                    self.logger.debug(' line parsing has done')
                    output_columns = line.split()
                    self.logger.debug(' Column parsing has done')
                    command_name = output_columns[0]
                    user = output_columns[len(output_columns) - 8]
                    process_time = output_columns[len(output_columns) - 6]
                    start_date = output_columns[len(output_columns) - 4] + ' ' + output_columns[
                        len(output_columns) - 3] + ' ' + output_columns[len(output_columns) - 2] + ' ' + \
                                 output_columns[len(output_columns) - 1]
                    self.logger.debug(
                        ' CommandExecutionInfoItem attributes are ready for adding to result list')
                    self.execute(
                        'echo "{ \\"p\\": \\"' + process_time + '\\", \\"c\\": \\"' + command_name + '\\", \\"u\\":\\"' + user + '\\", \\"s\\":\\"' + start_date + '\\"}" >> ' + self.file_path)
                    self.logger.debug(
                        ' CommandExecutionInfoItem is created and added to result list')
                    self.commands.append(command_name)
                    self.logger.debug(str(len(lines)) + '------------' + str(i))
                    self.execute('echo "," >> ' + self.file_path)
                    self.isRecordExist += 1
                    i += 1
                if i >= 1:
                    return 'Basarili'
                if self.isRecordExist > 0:
                    return 'Basarili'
                return None
            else:
                self.logger.debug(
                    ' lastcomm command has not return with a result')
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Uygulama çalıştırma bilgilerini getirirken beklenmedik hata!')
                return None

        except Exception as e:
            self.logger.debug('[ PACKAGE MANAGER ]Error in check_output method {}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Uygulama çalıştırma bilgilerini getirirken beklenmedik hata!')


class VersionInfoItem:
    def __init__(self, command_name, package_name, package_version):
        self.commandName = command_name
        self.packageName = package_name
        self.packageVersion = package_version


class CommandExecutionInfoItem:
    def __init__(self, command_name, user, process_time, start_date):
        self.commandName = command_name
        self.user = user
        self.processTime = process_time
        self.startDate = start_date


def handle_task(task, context):
    plugin = GetExecutionInfo(task, context)
    plugin.handle_task()
