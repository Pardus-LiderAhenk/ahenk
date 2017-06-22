#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: >
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class Browser(AbstractPlugin):
    """docstring for Browser"""

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.mozilla_config_file = 'mozilla.cfg'
        self.local_settings_JS_file = 'local-settings.js'
        self.local_settings_JS_path = 'defaults/pref/'
        self.logger.info('Parameters were initialized.')

    def handle_policy(self):
        self.logger.info('Browser plugin handling...')
        try:
            username = self.context.get('username')
            self.logger.info('Username: {}'.format(username))
            if username is not None:
                self.logger.debug('Writing preferences to user profile')
                self.write_to_user_profile(username)
                self.context.create_response(code=self.message_code.POLICY_PROCESSED.value, message='Kullanıcı browser profili başarıyla uygulandı.')
            else:
                self.logger.debug('Writing preferences to global profile')
                self.write_to_global_profile()
                self.context.create_response(code=self.message_code.POLICY_PROCESSED.value, message='Ajan browser profili başarıyla uygulandı.')
            self.logger.info('Browser profile is handled successfully')
        except Exception as e:
            self.logger.error('A problem occurred while handling browser profile: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value, message='Browser profili uygulanırken bir hata oluştu.')

    def write_to_user_profile(self, username):

        try:
            username = str(username).strip()
            profile_paths = self.find_user_preference_paths(username)

            # User might have multiple firefox profile directories
            for path in profile_paths:
                path = str(path) + '/user.js'
                user_jss = open(path, 'w')
                preferences = json.loads(self.data)['preferences']
                self.logger.debug('Writing preferences to user.js file ...')
                for pref in preferences:
                    if pref['value'].isdigit() or str(pref['value']) == 'false' or str(pref['value']) == 'true':
                        value = pref['value']
                    else:
                        value = '\"' + pref['value'] + '\"'
                    line = 'user_pref("' + str(pref['preferenceName']) + '",' + value + ');\n'
                    user_jss.write(line)

                self.logger.debug('User preferences were wrote successfully')
                user_jss.close()
                change_owner = 'chown ' + username + ':' + username + ' ' + path
                self.execute(change_owner)
                self.logger.debug('Preferences file owner is changed')

        except Exception as e:
            self.logger.error('A problem occurred while writing user profile: {0}'.format(str(e)))
            # Remove global lock files to tell Firefox to load the user file
        installation_path = self.find_firefox_installation_path()
        if installation_path is None:
            self.logger.error('Firefox installation directory could not be found! Finishing task...')
            return
        self.silent_remove(str(installation_path) + self.mozilla_config_file)
        self.silent_remove(str(installation_path) + self.local_settings_JS_path + self.local_settings_JS_file)
        self.logger.debug('User profiles have been set successfully')

    def write_to_global_profile(self):
        firefox_installation_path = self.find_firefox_installation_path()
        preferences = None
        try:
            preferences = json.loads(str(self.data))['preferences']
        except Exception as e:
            self.logger.error('Problem occurred while getting preferences. Error Message: {}'.format(str(e)))

        mozilla_cfg = open(str(firefox_installation_path) + self.mozilla_config_file, 'w')
        self.logger.debug('Mozilla configuration file is created')
        for pref in preferences:
            if pref['value'].isdigit() or str(pref['value']) == 'false' or str(pref['value']) == 'true':
                value = pref['value']
            else:
                value = '\"' + pref['value'] + '\"'
            line = 'lockPref("' + str(pref['preferenceName']) + '",' + value + ');\n'
            mozilla_cfg.write(line)
        mozilla_cfg.close()
        self.logger.debug('Preferences were wrote to Mozilla configuration file')

        local_settings_path = str(firefox_installation_path) + self.local_settings_JS_path
        if not self.is_exist(local_settings_path):
            self.logger.debug('Firefox local setting path not found, it will be created')
            self.create_directory(local_settings_path)
        local_settings_js = open(local_settings_path + self.local_settings_JS_file, 'w')
        local_settings_js.write(
                'pref("general.config.obscure_value", 0);\npref("general.config.filename", "mozilla.cfg");\n')
        local_settings_js.close()
        self.logger.debug('Firefox local settings were configured')

    def silent_remove(self, filename):
        try:
            if self.is_exist(filename):
                self.delete_file(filename)
                self.logger.debug('{0} removed successfully'.format(filename))
            else:
                self.logger.warning('{0} was tried to delete but not found.'.format(filename))
        except Exception as e:
            self.logger.error('Problem occurred while removing file {0}. Exception Message is: {1}'.format(filename, str(e)))

    def find_user_preference_paths(self, user_name):

        paths = []
        firefox_path = '/home/' + user_name + '/.mozilla/firefox/'
        profile_ini_file = open(firefox_path + 'profiles.ini', 'r')
        profile_ini_file_lines = profile_ini_file.readlines()
        for line in profile_ini_file_lines:
            if 'Path' in line:
                paths.append(firefox_path + str(line.split('=')[1]).strip())
        if len(paths) > 0:
            self.logger.debug('User preferences path found successfully')
            return paths
        else:
            self.logger.error('User preferences path not found')

    def find_firefox_installation_path(self):
        installation_path = '/usr/lib/firefox/'
        if not self.is_exist(installation_path):
            installation_path = '/opt/firefox/'
        if not self.is_exist(installation_path):
            installation_path = '/usr/lib/iceweasel/'
        if not self.is_exist(installation_path):
            self.logger.error('Firefox installation path not found')
            return None
        self.logger.debug('Firefox installation path found successfully')
        return installation_path


def handle_policy(profile_data, context):
    browser = Browser(profile_data, context)
    browser.handle_policy()
