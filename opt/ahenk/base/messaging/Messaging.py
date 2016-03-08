#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import sys,pwd,os
import datetime,json
sys.path.append('../..')
from base.Scope import Scope

class Messaging(object):

    def __init__(self):
        
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        self.event_manger=scope.getEventManager()

    #TODO can use sh commands for getting username and timestamp

    def login_msg(self):
        data = {}
        data['type'] = 'LOGIN'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data

    def logout_msg(self):
        data = {}
        data['type'] = 'LOGOUT'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data

    def get_policies_msg(self):
        data = {}
        data['type'] = 'GET_POLICIES'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data

    def unregister_msg(self):
        data = {}
        data['type'] = 'UNREGISTER'
        data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        return json_data
