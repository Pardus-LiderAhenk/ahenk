#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:  Ebru Arslan  <16ebruarslan@gmail.com>

import json
import os
from pathlib import Path
from base.plugin.abstract_plugin import AbstractPlugin

class BrowserChrome(AbstractPlugin):
    
    def __init__(self, data, context):
       super(AbstractPlugin, self).__init__()
       self.data = data
       self.context = context
       self.logger = self.get_logger()
       self.message_code = self.get_message_code()
       self.local_settings_path_suffix = 'policies/managed/'
       self.local_settings_path = '/etc/opt/chrome/'
       self.logger.info('Parameters were initialized.')
       self.user_js_file = "browser_chrome_preferences_{0}.json"

    def create_chrome_file(self):
        try:
            return  os.makedirs(self.local_settings_path+self.local_settings_path_suffix, mode=0o777, exist_ok=True)
        except:
            raise

    #def is_installed(package_name): ile true/false kontrol edilecek


    def handle_policy(self):
        self.logger.info('Browser Chrome plugin handling...')
        try:
            self.create_chrome_file()
            username = self.get_username()
            self.logger.info('Username: {}'.format(username))
            self.logger.debug('Writing preferences to user profile')
            self.write_to_profile()
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value, message='Kullanıcı browser chrome  profili başarıyla uygulandı.')
        except Exception as e:
            self.logger.error('A problem occurred while handling browser profile: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value, message='Browser Chrome profili uygulanırken bir hata oluştu.')

    def silent_remove(self, filename):
        try:
            if self.is_exist(filename):
                self.delete_file(filename)
                self.logger.debug('{0} removed successfully'.format(filename))
            else:
                self.logger.warning('{0} was tried to delete but not found.'.format(filename))
        except Exception as e:
            self.logger.error('Problem occurred while removing file {0}. Exception Message is: {1}'.format(filename, str(e)))


    def write_to_profile(self):
        username = self.get_username()
        path = self.local_settings_path+self.local_settings_path_suffix
        file = self.user_js_file.format(username)
        self.silent_remove(file)
        user_js = open(path + file, "w")
        preferences = json.loads(self.data)['preferencesChrome']
        print(type(preferences))
        self.logger.debug('Writing preferences chrome to file ...')
        user_js.write('{\n')
        for pref in preferences: 
            if pref['value'].isdigit() or str(pref['value']) == 'false' or str(pref['value']) == 'true':
                value = pref['value']
            else:
                value = '\"' + pref['value'] + '\"'
            #if ind == (len(preferences)-1):
            #    line = '"' + str(pref['preferenceName']) + '": ' + value + '\n'
            #else:
            #    line = '"' + str(pref['preferenceName']) + '": ' + value + ',\n'
            line = '"' + str(pref['preferenceName']) + '": ' + value + ',\n'
            user_js.write(line)
        user_js.write('\n}')

        self.logger.debug('User preferences were wrote successfully')
        user_js.close()


def handle_policy(profile_data, context):
    browser = BrowserChrome(profile_data, context)
    browser.handle_policy()
   
    