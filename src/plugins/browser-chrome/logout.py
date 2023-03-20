#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Ebru ARSLAN <ebru.arslan@pardus.org.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class Logout(AbstractPlugin):
    def __init__(self, context):
        super(Logout, self).__init__()
        self.context = context
        self.logger = self.get_logger()
        self.local_settings_path_suffix = 'policies/managed/'
        self.local_settings_path = '/etc/opt/chrome/'
        self.user_js_file = 'liderahenk_browser_chrome_preferences.json'
 
        self.logger.debug('Parameters were initialized.')
        self.username = self.get_username()
        if self.username is None:
            self.username = self.get_active_user()  

    def handle_logout_mode(self):
        profil_full_path = self.local_settings_path+self.local_settings_path_suffix+self.user_js_file
        if self.is_exist(profil_full_path):
            self.delete_file(profil_full_path)

        self.default_proxy_settings()

    def default_proxy_settings(self):
        username = self.get_username()
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


def handle_mode(context):
    logout = Logout(context)
    logout.handle_logout_mode()
