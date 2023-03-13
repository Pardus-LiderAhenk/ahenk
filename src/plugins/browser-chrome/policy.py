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
            self.write_to_profile()
            self.write_to_chrome_proxy()
            # try:
            #     self.write_to_chrome_proxy()
            # except Exception as e:
            #     self.logger.error(e)
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
        file_full_path = path + file
        self.silent_remove(file_full_path)
        self.create_file(file_full_path)
        preferences = json.loads(self.data)
        self.logger.debug('Writing preferences chrome to file ...')
        content = "{\n"
        for pref in preferences["preferencesChrome"]:
            self.logger.debug(pref)
            line = ""
            if pref["value"] == "false" or pref["value"] == "true":
                line = '"'+pref["preferenceName"]+'":' + str(pref["value"])+',\n'
            elif type(pref["value"]).__name__ == "int":
                line = '"'+pref["preferenceName"]+'":' + str(pref["value"])+',\n'
            else:
                line = '"'+pref["preferenceName"]+'":"' + str(pref["value"])+'",\n'
            content += line
            
        content += "\n}"
        self.write_file(file_full_path, content)

        self.logger.debug('User chrome preferences were wrote successfully')


    def write_to_chrome_proxy(self):
        proxy_full_path = self.local_settings_proxy_profile + self.local_settings_proxy_file
        self.silent_remove(proxy_full_path)
        self.create_file(proxy_full_path)
        proxy_preferences = json.loads(self.data)
        line = ""
        if len(proxy_preferences) > 0:
            proxy_data =  proxy_preferences["proxyListChrome"]
            self.logger.debug(proxy_data)
            if proxy_data[0].get('value') == '0' :
                line =  proxy_data[1].get('preferenceName')
                
            elif proxy_data[0].get('value') == '1':
                for proxy in proxy_data[1:5]:
                    line += str(proxy['preferenceName'] + "\n") 

            elif proxy_data[0].get('value') == '2':
                line =  proxy_data[1].get('preferenceName')    
            
            self.write_file(proxy_full_path, line)
            self.make_executable(proxy_full_path)
            self.execute_script(proxy_full_path)
        else:
             self.logger.debug("Proxy preferences files is empty!!")
        # subprocess.Popen('sudo chmod +x {0}'.format(proxy_sh), shell=True)
        self.logger.debug('User proxy preferences were wrote successfully')
          

#sudo chmod +x /etc/profile.d/proxy.sh

def handle_policy(profile_data, context):
    browser = BrowserChrome(profile_data, context)
    browser.handle_policy()
