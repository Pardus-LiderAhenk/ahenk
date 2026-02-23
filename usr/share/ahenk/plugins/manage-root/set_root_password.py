#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import json
import datetime
from base.plugin.abstract_plugin import AbstractPlugin
from base.model.enum.content_type import ContentType

class RootPassword(AbstractPlugin):
    def __init__(self, task, context):
        super(RootPassword, self).__init__()
        self.task = task
        self.context = context
        self.message_code = self.get_message_code()
        self.logger = self.get_logger()
        self.username = 'root'

    def save_mail(self, status):
        cols = ['command', 'mailstatus', 'timestamp']
        values = ['set_root_password', status, self.timestamp()]
        self.db_service.update('mail', cols, values)

    def set_mail(self, mail_content):
        if '{date}' in str(mail_content):
            mail_content = str(mail_content).replace('{date}', str(datetime.date.today()))
        if hasattr(self, 'Ahenk') and '{ahenk}' in str(mail_content):
            mail_content = str(mail_content).replace('{ahenk}', str(self.Ahenk.dn()))

        self.context.set_mail_content(mail_content)

    def handle_task(self):
        lockRootUser = self.task.get('lockRootUser', False)
        password = self.task.get('RootPassword', '')
        rootEntity = self.task.get('rootEntity', '')

        self.logger.debug('[Root Pass] Processing task...')

        mail_send = self.task.get('mailSend', False)
        mail_subject = self.task.get('mailSubject', '')
        mail_content = self.task.get('mailContent', '')

        try:
            if lockRootUser:
                self.logger.info("Locking root user")
                result_code, p_out, p_err = self.execute_command(['passwd', '-l', 'root'], shell=False)
                
                if result_code == 0:
                    self.logger.debug("Successfully locked root user")
                    self.context.create_response(
                        code=self.message_code.TASK_PROCESSED.value,
                        message='Root kullanıcısı başarıyla kilitlendi.',
                        data=json.dumps({'Result': p_out}),
                        content_type=ContentType.APPLICATION_JSON.value
                    )
                else:
                    self.logger.error("Failed to lock root user: " + str(p_err))
                    self.context.create_response(
                        code=self.message_code.TASK_ERROR.value,
                        message='Root kullanıcısı kilitlenirken hata oluştu!',
                        data=json.dumps({'Result': p_err}),
                        content_type=ContentType.APPLICATION_JSON.value
                    )

            else:
                if str(password).strip():
             
                    input_data = '{}:{}'.format(self.username, password)
                    result_code, p_out, p_err = self.execute_command(
                        ['chpasswd'], 
                        stdin=input_data.encode('utf-8'), 
                        shell=False
                    )

                    # self.set_mail(mail_content)

                    if result_code == 0:
                        self.logger.info('Successfully changed root password.')
                        self.context.create_response(
                            code=self.message_code.TASK_PROCESSED.value,
                            message='Parola başarı ile değiştirildi.',
                            data=json.dumps({
                                'Result': 'Parola başarı ile değiştirildi.',
                                'mail_content': str(self.context.get_mail_content()),
                                'mail_subject': str(self.context.get_mail_subject()),
                                'mail_send': self.context.is_mail_send(),
                                'rootEntity': rootEntity
                            }),
                            content_type=ContentType.APPLICATION_JSON.value
                        )
                    else:
                        self.logger.error("Failed to change password. Error: " + str(p_err))
                        self.context.create_response(
                            code=self.message_code.TASK_ERROR.value,
                            message='Parola değiştirilirken sistem hatası oluştu!',
                            data=json.dumps({'Result': str(p_err)}),
                            content_type=ContentType.APPLICATION_JSON.value
                        )
                else:
                    self.logger.warning("Password cannot be empty.")
                    self.context.create_response(
                        code=self.message_code.TASK_ERROR.value,
                        message='Parola boş olamaz.',
                        content_type=ContentType.APPLICATION_JSON.value
                    )

        except Exception as e:
            self.logger.error('Critical Error in RootPassword Plugin: {0}'.format(str(e)))
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message='İşlem sırasında beklenmedik bir hata oluştu.',
                data=json.dumps({'Error': str(e)}),
                content_type=ContentType.APPLICATION_JSON.value
            )

    def execute_command(self, command, stdin=None, env=None, cwd=None, shell=False):
        try:
            process = subprocess.Popen(
                command, 
                stdin=subprocess.PIPE if stdin else None, 
                env=env, 
                cwd=cwd, 
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE, 
                shell=shell
            )
            
            p_out, p_err = process.communicate(input=stdin)
            result_code = process.returncode
            p_out = p_out.decode("utf-8", errors="ignore") if p_out else ""
            p_err = p_err.decode("utf-8", errors="ignore") if p_err else ""

            return result_code, p_out, p_err

        except Exception as e:
            return 1, '', 'Could not execute command. Error: {0}'.format(str(e))

def handle_task(task, context):
    clz = RootPassword(task, context)
    clz.handle_task()
