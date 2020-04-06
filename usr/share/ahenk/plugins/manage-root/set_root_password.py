#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author: Tuncay Çolak <tuncay.colak@tubitak.gov.tr> <tncyclk05@gmail.com>
# Author: Hasan Kara <h.kara27@gmail.com>

import subprocess
from base.plugin.abstract_plugin import AbstractPlugin
from base.model.enum.content_type import ContentType
import json
import datetime

class RootPassword(AbstractPlugin):
    def __init__(self, task, context):
        super(RootPassword, self).__init__()
        self.task = task
        self.context = context
        self.message_code = self.get_message_code()
        self.logger = self.get_logger()
        self.create_shadow_password = 'mkpasswd {}'
        self.change_password = 'usermod -p {0} {1}'
        self.username= 'root'


    def save_mail(self, status):
        cols = ['command', 'mailstatus', 'timestamp'];
        values = ['set_root_password', status, self.timestamp()]
        self.db_service.update('mail', cols, values)

    def set_mail(self,mail_content):
        if mail_content.__contains__('{date}'):
            mail_content = str(mail_content).replace('{date}', str(datetime.date.today()));
        if mail_content.__contains__('{ahenk}'):
            mail_content = str(mail_content).replace('{ahenk}', str(self.Ahenk.dn()));

        self.context.set_mail_content(mail_content)

    def handle_task(self):
        lockRootUser = self.task['lockRootUser']
        password = self.task['RootPassword']
        rootEntity = self.task['rootEntity']

        self.logger.debug('[Root Pass] password:  ' + str("**********"))

        mail_send = False
        mail_subject = ''
        mail_content = ''

        if 'mailSend' in self.task:
            mail_send = self.task['mailSend'];
        if 'mailSubject' in self.task:
            mail_subject = self.task['mailSubject'];
        if 'mailContent' in self.task:
            mail_content = self.task['mailContent'];
        try:
            if lockRootUser:
                self.logger.info("Locking root user")
                result_code, p_out, p_err = self.execute_command("passwd -l root")
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Root kullanıcısı başarıyla kilitlendi.',
                                             data=json.dumps({'Result': p_out}),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                if str(password).strip() != '':
                    result_code, p_out, p_err = self.execute_command(self.create_shadow_password.format(password))
                    shadow_password = p_out.strip()
                    self.execute_command(self.change_password.format('\'{}\''.format(shadow_password), self.username))
                    self.set_mail(mail_content)
                    self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                                 message='Parola Başarı ile değiştirildi.',
                                                 data=json.dumps({
                                                     'Result': 'Parola Başarı ile değiştirildi.',
                                                     'mail_content': str(self.context.get_mail_content()),
                                                     'mail_subject': str(self.context.get_mail_subject()),
                                                     'mail_send': self.context.is_mail_send(),
                                                     'rootEntity': rootEntity
                                                 }),
                                                 content_type=ContentType.APPLICATION_JSON.value)
                    self.logger.debug('Changed password.')

        except Exception as e:
            self.logger.error('Error: {0}'.format(str(e)))
            mail_content = 'Root Parolası değiştirlirken hata oluştu.'
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Parola değiştirilirken hata oluştu.',
                                         data=json.dumps({
                                             'Result': 'Parola değiştirilirken hata oluştu.',
                                             'mail_content': str(self.context.get_mail_content()),
                                             'mail_subject': str(self.context.get_mail_subject()),
                                             'mail_send': self.context.is_mail_send(),
                                             'rootEntity': rootEntity
                                         }),
                                         content_type=ContentType.APPLICATION_JSON.value)

    ## this methode is only for manage-root password plugin
    def execute_command(self, command, stdin=None, env=None, cwd=None, shell=True, result=True):

        try:
            process = subprocess.Popen(command, stdin=stdin, env=env, cwd=cwd, stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE, shell=shell)

            self.logger.debug('Executing command for manage-root')

            if result is True:
                result_code = process.wait()
                p_out = process.stdout.read().decode("unicode_escape")
                p_err = process.stderr.read().decode("unicode_escape")

                return result_code, p_out, p_err
            else:
                return None, None, None
        except Exception as e:
            return 1, 'Could not execute command: {0}. Error Message: {1}'.format(command, str(e)), ''




def handle_task(task, context):
    clz = RootPassword(task, context)
    clz.handle_task()
