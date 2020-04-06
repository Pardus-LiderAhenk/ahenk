#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import configparser
import datetime
import json

from base.plugin.abstract_plugin import AbstractPlugin


class LoginManager(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.username = self.context.get('username')

        self.parameters = json.loads(self.data)

        self.days = self.parameters['days']
        self.start_time = self.parameters['start-time']
        self.end_time = self.parameters['end-time']
        self.last_date = datetime.datetime.strptime(str(self.parameters['last-date']), "%d/%m/%Y").date()
        self.duration = self.parameters['duration']

        self.command_cron_control = 'crontab -l | grep login-manager/scripts/{}'

        self.logger.debug('Parameters were initialized.')

    def handle_policy(self):
        try:
            config = configparser.RawConfigParser()
            config.add_section('PERMISSION')

            config.set('PERMISSION', 'days', str(self.days))
            config.set('PERMISSION', 'start_time', str(self.start_time))
            config.set('PERMISSION', 'end_time', str(self.end_time))
            config.set('PERMISSION', 'last_date', str(self.last_date))
            config.set('PERMISSION', 'duration', str(self.duration))

            if not self.is_exist('{0}login-manager/login_files'.format(self.Ahenk.plugins_path())):
                self.create_directory('{0}login-manager/login_files'.format(self.Ahenk.plugins_path()))

            with open('{0}login-manager/login_files/{1}.permissions'.format(self.Ahenk.plugins_path(), self.username),
                      'w') as configfile:
                self.logger.debug('Writing parameters to configuration file...')
                config.write(configfile)

            self.logger.debug('Making scripts executable...')
            self.make_executable('{0}login-manager/scripts/cron.sh'.format(self.Ahenk.plugins_path()))
            self.make_executable('{0}login-manager/scripts/check.py'.format(self.Ahenk.plugins_path()))

            self.logger.debug('Initial control for login permissions...')
            self.execute('/usr/bin/python3 {0}login-manager/scripts/check.py {0}'.format(self.Ahenk.plugins_path()))

            result_code, p_out, p_err = self.execute(self.command_cron_control.format('check.py'))

            if p_out == '':
                self.logger.debug('Creating a cron job to check session every minute...')
                self.execute_script('{0}login-manager/scripts/cron.sh'.format(self.Ahenk.plugins_path()), [
                    '* * * * * /usr/bin/python3 {0}login-manager/scripts/check.py {0}'.format(
                        self.Ahenk.plugins_path())])

            self.logger.info('Session check has been started.')
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value,
                                         message='Oturum kontrolü başlatıldı.')


        except Exception as e:
            self.logger.error(
                'A problem occured while handling Login-Manager policy: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value,
                                         message='Login-Manager profili uygulanırken bir hata oluştu.')


def handle_policy(profile_data, context):
    manage = LoginManager(profile_data, context)
    manage.handle_policy()
