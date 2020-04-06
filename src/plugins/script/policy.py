# !/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Hasan Kara

import json

from base.plugin.abstract_plugin import AbstractPlugin


class Script(AbstractPlugin):
    def __init__(self, data, context):
        super(Script, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.machine_profile = True
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.temp_file_name = str(self.generate_uuid())
        self.base_file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)

    def handle_policy(self):
        try:
            json_data = json.loads(self.data)

            script_type = str(json_data['SCRIPT_TYPE'])
            script_contents = self.format_contents(str(json_data['SCRIPT_CONTENTS']))
            script_params = str(json_data['SCRIPT_PARAMS'])
            file_path = self.base_file_path

            # Determine script extension and command
            command = ''
            if script_type == 'BASH':
                file_path += '.sh'
                command += 'bash'
            elif script_type == 'PYTHON':
                file_path += '.py'
                command += 'python'
            elif script_type == 'PERL':
                file_path += '.pl'
                command += 'perl'
            elif script_type == 'RUBY':
                file_path += '.rb'
                command += 'ruby'

            self.create_script_file(file_path, script_contents)

            result_code, p_out, p_err = self.execute_script_file(command, file_path, script_params)
            if result_code != 0:
                self.logger.error("Error occurred while executing script: " + str(p_err))
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Betik çalıştırılırken hata oluştu',
                                             data=json.dumps({'Result': p_err}),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                self.logger.debug("Executed script file.")
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Betik başarıyla çalıştırıldı.',
                                             data=json.dumps({'Result': p_out}),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Betik çalıştırılırken hata oluştu:' + str(e),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

    def create_script_file(self, file_path, script_contents):
        self.logger.debug("Creating script file.")
        # Create temporary script file with the provided content
        self.write_file(file_path, script_contents)

        # Make the file executable
        self.make_executable(file_path)
        self.logger.debug("Created script file: {0}".format(file_path))

    def execute_script_file(self, command, file_path, script_params):
        self.logger.debug("Executing script file.")
        # Execute the file
        if not script_params:
            return self.execute('{0} {1}'.format(command, file_path))
        else:
            return self.execute('{0} {1} {2}'.format(command, file_path, script_params))

    @staticmethod
    def format_contents(contents):
        tmp = contents
        replacements = list()
        replacements.append(('&dbq;', '\"'))
        replacements.append(('&sgq;', '\''))
        for r, n in replacements:
            tmp = tmp.replace(r, n)
        return tmp



def handle_policy(profile_data, context):
    plugin = Script(profile_data, context)
    plugin.handle_policy()
