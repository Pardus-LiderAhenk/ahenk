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
        self.user_js_file = "liderahenk_browser_chrome_preferences.json"
 
        self.logger.info('Parameters were initialized.')

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
        file_full_path = self.local_settings_path+self.local_settings_path_suffix+self.user_js_file
        self.silent_remove(file_full_path)
        self.create_file(file_full_path)
        preferences = json.loads(self.data)
        self.logger.debug('Writing preferences chrome to file ...')
        content = "{\n"
        for pref in preferences["preferencesChrome"]:
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
        #self.default_proxy_settings()
        proxy_type = "0"
        proxy_preferences = json.loads(self.data)
        username = self.get_username()
        if username is None:
            username = self.get_active_user()  
        if len(proxy_preferences) > 0:
            proxy_data =  proxy_preferences["proxyListChrome"]
            for pref in proxy_data:
                if pref["preferenceName"] == "type":
                    proxy_type = pref['value']
                    
            if proxy_type == '0':
                self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy mode 'none''".format(username))
            elif proxy_type == '1':
                self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy mode 'manual''".format(username))
                for pref in proxy_data:
                    if pref["preferenceName"] == "httpHost":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http host '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "httpPort":
                        self.execute("su - {0} -c  ' gsettings set org.gnome.system.proxy.http port '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "httpsHost":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.https host '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "httpsPort":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.https port '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "ftpHost":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.ftp host '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "ftpPort":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.ftp port '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "socksHost":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.socks port '{1}''".format(username,str(pref['value'])))
                    if pref["preferenceName"] == "socksPort":
                        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.socks port '{1}''".format(username,str(pref['value'])))
            elif proxy_type == '2':
                self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy mode 'auto''".format(username))
                self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy autoconfig-url '{1}''".format(username,str(pref['value'])))
                
        else:
             self.logger.debug("Proxy preferences files is empty!!")
        self.logger.debug('User proxy preferences were wrote successfully')

    def default_proxy_settings(self):
        username = self.get_username()
        if username is None:
            username = self.get_active_user()  
        if (self.execute("su - {0} -c  'gsettings get org.gnome.system.proxy mode'".format(self.username))) != 'none':
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy autoconfig-url '''".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy ignore-hosts ['localhost', '127.0.0.0/8']".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy mode 'none''".format(username))
            #self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy use-same-proxy true'".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.ftp host '''".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.ftp port 0'".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http host '''".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http port 8080'".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.https host '''".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.https port 0'".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.socks host '''".format(username))
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.socks port 0'".format(username))
            #self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http use-authentication false'".format(username))

def handle_policy(profile_data, context):
    browser = BrowserChrome(profile_data, context)
    browser.handle_policy()
