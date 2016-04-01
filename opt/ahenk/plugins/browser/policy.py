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

        # if (is_user):
        #   self.write_to_user_profile(prefsText, userNameArray, task)
        # else:
        self.write_to_global_profile()

    def write_to_user_profile(self, prefs_text, user_name_array):
        pass

    def write_to_global_profile(self):
        #TODO NEED DEBUG
        firefox_installation_path = self.find_firefox_installation_path()
        preferences = json.loads(self.data['preferences'])

        print(str(firefox_installation_path))
        print("W1111" + str(firefox_installation_path) + self.mozilla_config_file)

        mozilla_cfg = open(str(firefox_installation_path) + self.mozilla_config_file, 'w')
        print(str(firefox_installation_path) + self.mozilla_config_file)

        for pref in preferences:
            if isinstance(pref['value'], int) is True or isinstance(pref['value'], bool) is True or str(pref['value']) is 'false' or str(pref['value']) is 'true':
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
        local_settings_js.write('pref("general.config.obscure_value", 0);\npref("general.config.filename", "mozilla.cfg");\n')
        local_settings_js.close()

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
