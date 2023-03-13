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
        self.local_settings_proxy_profile = '/etc/profile.d/'
        self.local_settings_proxy_file = 'liderahenk_chrome_proxy.sh'
        self.logger.info('Parameters were initialized.')
        self.user_js_file = "browser_chrome_preferences_{0}.json"
 
        self.logger.debug('Parameters were initialized.')

    def handle_logout_mode(self):
        username = self.get_username()
        profil_full_path = self.local_settings_path+self.local_settings_path_suffix+self.user_js_file.format(username)
        profil_proxy_path = self.local_settings_proxy_profile+self.local_settings_proxy_file
        if self.is_exist(profil_full_path):
            self.delete_file(profil_full_path)
        if self.is_exist(profil_proxy_path):
            self.delete_file(profil_proxy_path)


def handle_mode(context):
    logout = Logout(context)
    logout.handle_logout_mode()
