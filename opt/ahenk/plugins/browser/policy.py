#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: >
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import os
from base.plugin.AbstractCommand import AbstractCommand


class Browser(AbstractCommand):
    """docstring for Browser"""

    def __init__(self, data, context):
        super(Browser, self).__init__()
        self.data = data
        self.context = context
        self.mozilla_config_file = 'mozilla.cfg'
        self.local_settings_JS_file = 'local-settings.js'
        self.local_settings_JS_path = 'defaults/pref/'

    def handle_policy(self):

        print("Browser handling")

        username = None
        if username is not None:
            self.write_to_user_profile(username)
        else:
            self.write_to_global_profile()

        #prefsText -lockPrefsText

    def write_to_user_profile(self, username):

        try:
            username = str(username).strip()
            profile_paths = self.find_user_preference_paths(username)

            # User might have multiple firefox profile directories
            for path in profile_paths:
                path = str(path) + '/user.js'
                userjss = open(path, 'w')
                userjss.write("prefsText")
                userjss.close()
                changeOwner = 'chown ' + username + ':' + username + ' ' + path
                #TODO(result_code, p_out, p_err) = self.execute_command(changeOwner, shell=True)
        except Exception as e:
            print('ERR1')
            # Remove global lock files to tell Firefox to load the user file
            installation_path = self.find_firefox_installation_path()
            if installation_path is None:
                return
            self.silent_remove(str(installation_path) + self.mozilla_config_file)
            self.silent_remove(str(installation_path) + self.local_settings_JS_path + self.local_settings_JS_file)

    def write_to_global_profile(self):
        # TODO NEED DEBUG
        firefox_installation_path = self.find_firefox_installation_path()
        preferences = json.loads(self.data['preferences'])

        print(str(firefox_installation_path))
        print("W1111" + str(firefox_installation_path) + self.mozilla_config_file)

        mozilla_cfg = open(str(firefox_installation_path) + self.mozilla_config_file, 'w')
        print(str(firefox_installation_path) + self.mozilla_config_file)

        for pref in preferences:
            if isinstance(pref['value'], int) is True or isinstance(pref['value'], bool) is True or str(
                    pref['value']) is 'false' or str(pref['value']) is 'true':
                value = pref['value']
            else:
                value = '"' + pref['value'] + '"'
            line = 'lockPref("' + str(pref['preferenceName']) + '",' + value + ');\n'
            mozilla_cfg.write(line)
        mozilla_cfg.close()

        print("close")

        local_settings_path = str(firefox_installation_path) + self.local_settings_JS_path

        print("W2222" + local_settings_path)
        if not os.path.exists(local_settings_path):
            os.makedirs(local_settings_path)

        local_settings_js = open(local_settings_path + self.local_settings_JS_file, 'w')
        local_settings_js.write(
            'pref("general.config.obscure_value", 0);\npref("general.config.filename", "mozilla.cfg");\n')
        local_settings_js.close()

    def silent_remove(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            print('ERR2')

    def find_user_preference_paths(self, userName):
        paths = []
        firefox_path = '/home/' + userName + '/.mozilla/firefox/'
        profile_ini_file = open(firefox_path + 'profiles.ini', 'r')
        profile_ini_file_lines = profile_ini_file.readlines()
        for line in profile_ini_file_lines:
            if 'Path' in line:
                paths.append(firefox_path + str(line.split('=')[1]).strip())
        return paths

    def find_firefox_installation_path(self):
        installation_path = '/usr/lib/firefox/'
        if not os.path.exists(installation_path):
            installation_path = '/opt/firefox/'
        if not os.path.exists(installation_path):
            installation_path = '/usr/lib/iceweasel/'
        if not os.path.exists(installation_path):
            return None
        return installation_path


def handle_policy(profile_data, context):
    browser = Browser(profile_data, context)
    browser.handle_policy()
    print("This is policy file - BROWSER")
