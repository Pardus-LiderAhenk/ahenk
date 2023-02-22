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
       self.local_settings_proxy_profile = '/etc/profile.d/'
       self.local_settings_proxy_file = 'liderahenk_chrome_proxy.sh'
       self.logger.info('Parameters were initialized.')
       self.user_js_file = "browser_chrome_preferences_{0}.json"

    def create_chrome_file(self):
        try:
            return  os.makedirs(self.local_settings_path+self.local_settings_path_suffix, mode=0o777, exist_ok=True)
        except:
            raise

    def handle_policy(self):
        self.logger.info('Browser Chrome plugin handling...')
        try:
            self.create_chrome_file()
            username = self.get_username()
            self.logger.info('Username: {}'.format(username))
            self.logger.debug('Writing preferences to user profile')
            #self.write_to_profile()
            try:
                self.write_to_chrome_proxy()
            except Exception as e:
                self.logger.error(e)
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value, message='Kullanıcı browser chrome  profili başarıyla uygulandı.')
        except Exception as e:
            self.logger.error('A problem occurred while handling chrome browser profile: {0}'.format(str(e)))
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
        user_js = open(path + file, "a")
        preferences = json.loads(self.data)['preferencesChrome']
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

        self.logger.debug('User chrome preferences were wrote successfully')
        user_js.close()


    def write_to_chrome_proxy(self):
        proxy_full_path = self.local_settings_proxy_profile + self.local_settings_proxy_file
        self.silent_remove(proxy_full_path)
        # proxy preference lenght bak varsa çalıştır yoksa passs
        proxy_preferences = json.loads(self.data)['proxyListChrome']
        self.logger.debug(proxy_preferences)
        proxy_sh = self.create_file(proxy_full_path)
        content = ""
        for proxy in proxy_preferences:

            if proxy['value'].isdigit() or str(proxy['value']) == 'false' or str(proxy['value']) == 'true':
                value = proxy['value']
            else:
                value = '\"' + proxy['value'] + '\"'
            line = '"' + str(proxy['preferenceName']) + '": ' + value + ',\n'
            content += line
            self.logger.debug(content)
        
        self.write_file(proxy_full_path, content)
        self.execute_script(proxy_full_path)
        # subprocess.Popen('sudo chmod +x {0}'.format(proxy_sh), shell=True)
        self.logger.debug('User proxy preferences were wrote successfully')
          

#sudo chmod +x /etc/profile.d/proxy.sh

def handle_policy(profile_data, context):
    browser = BrowserChrome(profile_data, context)
    browser.handle_policy()
   
    
