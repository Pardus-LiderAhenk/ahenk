#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
from base.scope import Scope


class Mail:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.configuration_manager = scope.get_configuration_manager()
        try:
            self.smtp_host = self.configuration_manager.get('MAIL', 'smtp_host')
            self.smtp_port = int(self.configuration_manager.get('MAIL', 'smtp_port'))
            self.from_username = self.configuration_manager.get('MAIL', 'from_username')
            self.from_password = self.configuration_manager.get('MAIL', 'from_password')
            self.to_address = self.configuration_manager.get('MAIL', 'to_address')

        except Exception as e:
            self.logger.error(
                'A problem occurred while reading mail server parameters from conf file. Error Message: {0}'.format(
                    e))
        self.server = None
        self.logger.debug('Mail service initialized.')

    def connect(self):
        self.logger.debug('Connecting to SMTP server')
        self.server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        self.logger.debug('Setting debug level')
        self.server.set_debuglevel(2)
        self.logger.debug('Using tls if server supports')
        self.server.starttls()
        self.logger.debug('Loging in to smtp server as {0}'.format(self.from_username))
        self.server.login(self.from_username, self.from_password)

    def disconnect(self):
        self.logger.debug('Disconnecting from mail server')
        self.server.quit()
        self.logger.debug('Disconnected')

    def send_mail(self, subject, message, files=None):

        if files is None:
            files = []

        msg = MIMEMultipart()
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(message))

        # TODO files attachment max size
        if files is not None:
            for f in files:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(f, "rb").read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
                msg.attach(part)

        self.logger.debug('Sending mail to {0} {1}'.format(self.to_address, ' about {0}'.format(subject)))
        self.server.sendmail(self.from_username, self.to_address, msg.as_string())
        self.logger.debug('Mail was sent.')
