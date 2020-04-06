#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import configparser
import datetime
import glob
import logging
import os
import subprocess, time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from base.util.util import Util


class CheckTime:
    def __init__(self):
        super(self.__class__, self).__init__()

        if not os.path.exists('{0}login-manager/logs'.format(sys.argv[1])):
            os.makedirs('{0}login-manager/logs'.format(sys.argv[1]))

        logging.basicConfig(filename='{0}login-manager/logs/check.log'.format(sys.argv[1]), filemode='w',
                            level=logging.DEBUG)

        self.files = glob.glob('{0}login-manager/login_files/*.permissions'.format(sys.argv[1]))

        self.username = 'None'

        self.days = ''
        self.start_time = ''
        self.end_time = ''
        self.last_date = ''
        self.duration = ''

        self.arr_start_time = ''
        self.arr_end_time = ''

        self.today = datetime.datetime.today().weekday()
        self.current_time = datetime.datetime.today().time()
        self.current_date = datetime.datetime.today().date()

        self.start_minute = ''
        self.end_minute = ''
        self.current_minute = ''

        self.command_logout_user = 'killall --user {0}'
        self.command_get_users_currently_login = "who | cut -d' ' -f1 | sort | uniq"

        logging.debug('Parameters  were initialized.')

    def handle(self):
        try:

            for file in self.files:
                permission_file = str(file).replace('{0}login-manager/login_files/'.format(sys.argv[1]), '')
                self.username = permission_file.replace('.permissions', '')

                config_parser = configparser.ConfigParser()
                config_parser.read(file)

                logging.debug('Getting parameters from permission file for user \'{0}\''.format(self.username))

                self.days = config_parser.get('PERMISSION', 'days')
                self.start_time = config_parser.get('PERMISSION', 'start_time')
                self.end_time = config_parser.get('PERMISSION', 'end_time')
                self.last_date = datetime.datetime.strptime(str(config_parser.get('PERMISSION', 'last_date')),
                                                            "%Y-%m-%d").date()
                self.duration = config_parser.get('PERMISSION', 'duration')

                logging.debug(
                    'Days: {0}, Start Time: {1}, End Time: {2}, Last Date: {3}, Duration between notify and logout: {4}'.format(
                        self.days, self.start_time, self.end_time, self.last_date, self.duration))

                self.arr_start_time = str(self.start_time).split(':')
                self.arr_end_time = str(self.end_time).split(':')

                self.start_minute = int(self.arr_start_time[0]) * 60 + int(self.arr_start_time[1])
                self.end_minute = int(self.arr_end_time[0]) * 60 + int(self.arr_end_time[1])
                self.current_minute = int(self.current_time.hour) * 60 + int(self.current_time.minute)

                if self.username != 'None':
                    logging.debug('Writing to user profile...')
                    self.write_to_user_profile()
                else:
                    logging.debug('Writing to global profile...')
                    self.write_to_global_profile()

        except Exception as e:
            logging.error(e)

    def write_to_user_profile(self):
        if str(self.today) in self.days:

            if not (self.start_minute < self.current_minute < self.end_minute and self.current_date <= self.last_date):
                logging.debug('User \'{0}\' will log out.'.format(self.username))
                process = subprocess.Popen(self.command_logout_user.format(self.username), stdin=None, env=None,
                                           cwd=None, stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE, shell=True)
                process.wait()

            elif int(self.end_minute) - int(self.current_minute) == int(self.duration):
                Util.send_notify('Lider Ahenk',
                                 'Oturum {0} dakika sonra kapatılacak!'.format(str(self.duration)),
                                 ':0',
                                 self.username)
        else:
            Util.send_notify('Lider Ahenk',
                             'Oturum şimdi kapatılacak!',
                             ':0',
                             self.username)
            time.sleep(5)
            logging.debug('User \'{0}\' will log out.'.format(self.username))
            process = subprocess.Popen(self.command_logout_user.format(self.username), stdin=None, env=None, cwd=None,
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE, shell=True)
            process.wait()

    def write_to_global_profile(self):

        process = subprocess.Popen(self.command_get_users_currently_login, stdin=None, env=None, cwd=None,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE, shell=True)
        process.wait()
        p_out = process.stdout.read().decode("unicode_escape")
        users = []

        if p_out != None:
            users = str(p_out).split('\n')
            users.pop()

            if 'root' in users:
                users.remove('root')

        logging.debug('Logged-in users: {0}'.format(users))

        if str(self.today) in self.days:

            if not (self.start_minute < self.current_minute < self.end_minute and self.current_date <= self.last_date):
                for user in users:
                    logging.debug('User \'{0}\' will log out.'.format(user))
                    process = subprocess.Popen(self.command_logout_user.format(user), stdin=None, env=None, cwd=None,
                                               stderr=subprocess.PIPE,
                                               stdout=subprocess.PIPE, shell=True)
                    process.wait()

            elif int(self.end_minute) - int(self.current_minute) == int(self.duration):
                for user in users:
                    Util.send_notify('Lider Ahenk',
                                     'Oturum {0} dakika sonra kapatılacak!'.format(str(self.duration)),
                                     ':0',
                                     user)
                pass
        else:
            for user in users:
                Util.send_notify('Lider Ahenk',
                                 'Oturum şimdi kapatılacak!',
                                 ':0',
                                 user)
                logging.debug('User \'{0}\' will log out.'.format(user))
                process = subprocess.Popen(self.command_logout_user.format(user), stdin=None, env=None, cwd=None,
                                           stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE, shell=True)
                process.wait()


check = CheckTime()
check.handle()
