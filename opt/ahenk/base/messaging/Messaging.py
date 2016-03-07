#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import sys,pwd,os
import datetime,json
sys.path.append('../..')
from base.Scope import Scope

class Messaging(object):

    def __init__(self):
        print("messaging initilaziton")
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        self.event_manger=scope.getEventManager()

    def login_msg(self):
        data = {}
        data['type'] = 'login'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data

    def logout_msg(self):
        data = {}
        data['type'] = 'logout'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data

    def get_policies_msg(self):
        data = {}
        data['type'] = 'get_policies'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data

    def unregister_msg(self):
        data = {}
        data['type'] = 'registration'
        data['status'] = 'unregister'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data
