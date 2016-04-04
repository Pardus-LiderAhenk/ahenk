#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: >
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import os

from base.plugin.AbstractCommand import AbstractCommand
from base.model.MessageType import MessageType
from base.model.MessageCode import MessageCode


class Browser(AbstractCommand):
    """docstring for Browser"""

    def __init__(self, data, context):
        super(Browser, self).__init__()
        self.data = data
        self.context = context
        self.mozilla_config_file = 'mozilla.cfg'
        self.local_settings_JS_file = 'local-settings.js'
        self.local_settings_JS_path = 'defaults/pref/'
        self.logger = self.scope.getLogger()

    def handle_policy(self):

        self.logger.info('[Browser] Browser plugin handling...')
        try:
            username = self.context.get('username')
            if username is not None:
                self.logger.debug('[Browser] Writing preferences to user profile')
                self.write_to_user_profile(username)
                self.set_result(MessageType.POLICY_STATUS, MessageCode.POLICY_PROCESSED, 'User browser profile processed successfully')

            else:
                self.logger.debug('[Browser] Writing preferences to global profile')
                self.write_to_global_profile()
                self.set_result(MessageType.POLICY_STATUS, MessageCode.POLICY_PROCESSED, 'Agent browser profile processed successfully')
            self.logger.info('[Browser] Browser profile is handled successfully')
        except Exception as e:
            self.logger.error('[Browser] A problem occured while handling browser profile: {0}'.format(str(e)))
            self.set_result(MessageType.POLICY_STATUS, MessageCode.POLICY_ERROR, 'A problem occured while handling browser profile: {0}'.format(str(e)))

    def write_to_user_profile(self, username):

        try:
            username = str(username).strip()
            profile_paths = self.find_user_preference_paths(username)

            # User might have multiple firefox profile directories
            for path in profile_paths:
                path = str(path) + '/user.js'
                user_jss = open(path, 'w')
                preferences = json.loads(self.data['preferences'])
                self.logger.debug('[Browser] Writing preferences to user.js file ...')
                for pref in preferences:
                    if pref['value'].isdigit() or str(pref['value']) == 'false' or str(pref['value']) == 'true':
                        value = pref['value']
                    else:
                        value = '\"' + pref['value'] + '\"'
                    line = 'user_pref("' + str(pref['preferenceName']) + '",' + value + ');\n'
                    user_jss.write(line)

                self.logger.debug('[Browser] User preferences were wrote successfully')
                user_jss.close()
                change_owner = 'chown ' + username + ':' + username + ' ' + path
                self.context.execute(change_owner)
                self.logger.debug('[Browser] Preferences file owner is changed')

        except Exception as e:
            self.logger.error('[Browser] A problem occured while writing user profile: {0}'.format(str(e)))
            # Remove global lock files to tell Firefox to load the user file
        installation_path = self.find_firefox_installation_path()
        if installation_path is None:
            self.logger.error('[Browser] Firefox installation directory could not be found! Finishing task...')
            return
        self.silent_remove(str(installation_path) + self.mozilla_config_file)
        self.silent_remove(str(installation_path) + self.local_settings_JS_path + self.local_settings_JS_file)
        self.logger.debug('[Browser] User profiles have been set successfully')

    def write_to_global_profile(self):
        firefox_installation_path = self.find_firefox_installation_path()
        preferences = json.loads(self.data['preferences'])

        mozilla_cfg = open(str(firefox_installation_path) + self.mozilla_config_file, 'w')
        self.logger.debug('[Browser] Mozilla configuration file is created')
        for pref in preferences:
            if pref['value'].isdigit() or str(pref['value']) == 'false' or str(pref['value']) == 'true':
                value = pref['value']
            else:
                value = '\"' + pref['value'] + '\"'
            line = 'lockPref("' + str(pref['preferenceName']) + '",' + value + ');\n'
            mozilla_cfg.write(line)
        mozilla_cfg.close()
        self.logger.debug('[Browser] Preferences were wrote to Mozilla configuration file')

        local_settings_path = str(firefox_installation_path) + self.local_settings_JS_path
        if not os.path.exists(local_settings_path):
            self.logger.debug('[Browser] Firefox local setting path not found, it will be created')
            os.makedirs(local_settings_path)
        local_settings_js = open(local_settings_path + self.local_settings_JS_file, 'w')
        local_settings_js.write(
            'pref("general.config.obscure_value", 0);\npref("general.config.filename", "mozilla.cfg");\n')
        local_settings_js.close()
        self.logger.debug('[Browser] Firefox local settings were configured')

    def silent_remove(self, filename):
        try:
            os.remove(filename)
            self.logger.debug('[Browser] {0} removed successfully'.format(filename))
        except OSError as e:
            self.logger.error('[Browser] Problem occured while removing file: {0}. Exception is: {1}'.format(filename, str(e)))

    def find_user_preference_paths(self, user_name):

        paths = []
        firefox_path = '/home/' + user_name + '/.mozilla/firefox/'
        profile_ini_file = open(firefox_path + 'profiles.ini', 'r')
        profile_ini_file_lines = profile_ini_file.readlines()
        for line in profile_ini_file_lines:
            if 'Path' in line:
                paths.append(firefox_path + str(line.split('=')[1]).strip())
        if len(paths) > 0:
            self.logger.debug('[Browser] User preferences path found successfully')
            return paths
        else:
            self.logger.error('[Browser] User preferences path not found')

    def find_firefox_installation_path(self):
        installation_path = '/usr/lib/firefox/'
        if not os.path.exists(installation_path):
            installation_path = '/opt/firefox/'
        if not os.path.exists(installation_path):
            installation_path = '/usr/lib/iceweasel/'
        if not os.path.exists(installation_path):
            self.logger.error('[Browser] Firefox installation path not found')
            return None
        self.logger.debug('[Browser] Firefox installation path found successfully')
        return installation_path

    def set_result(self, type=None, code=None, message=None, data=None, content_type=None):
        self.context.put('message_type', type)
        self.context.put('message_code', code)
        self.context.put('message', message)
        # self.context.put('data')
        # self.context.put('content_type')


def handle_policy(profile_data, context):
    browser = Browser(profile_data, context)
    browser.handle_policy()
    print("This is policy file - BROWSER")
