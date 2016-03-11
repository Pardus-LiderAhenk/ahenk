#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import sys, pwd, os, datetime, json

sys.path.append('../..')
from base.Scope import Scope


class Messaging(object):
    def __init__(self):
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.conf_manager = scope.getConfigurationManager()
        self.event_manger = scope.getEventManager()

    # TODO can use sh commands or api for getting username and timestamp

    def login_msg(self):
        data = {}
        data['type'] = 'LOGIN'
        data['username'] = str(pwd.getpwuid(os.getuid())[0])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Login message was created')
        return json_data

    def logout_msg(self):
        data = {}
        data['type'] = 'LOGOUT'
        data['username'] = str(pwd.getpwuid(os.getuid())[0])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Logout message was created')
        return json_data

    def policies_msg(self):
        data = {}
        data['type'] = 'GET_POLICIES'
        data['username'] = str(pwd.getpwuid(os.getuid())[0])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Get Policies message was created')
        return json_data

    def registration_msg(self):
        data = {}
        data['type'] = 'REGISTER'
        data['from'] = str(self.conf_manager.get('REGISTRATION', 'from'))
        data['password'] = str(self.conf_manager.get('REGISTRATION', 'password'))
        data['macAddresses'] = str(self.conf_manager.get('REGISTRATION', 'macAddresses'))
        data['ipAddresses'] = str(self.conf_manager.get('REGISTRATION', 'ipAddresses'))
        data['hostname'] = str(self.conf_manager.get('REGISTRATION', 'hostname'))
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Registration message was created')
        return json_data

    def ldap_registration_msg(self):
        data = {}
        data['type'] = 'REGISTER_LDAP'
        data['from'] = str(self.conf_manager.get('REGISTRATION', 'from'))
        data['password'] = str(self.conf_manager.get('REGISTRATION', 'password'))
        data['macAddresses'] = str(self.conf_manager.get('REGISTRATION', 'macAddresses'))
        data['ipAddresses'] = str(self.conf_manager.get('REGISTRATION', 'ipAddresses'))
        data['hostname'] = str(self.conf_manager.get('REGISTRATION', 'hostname'))
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] LDAP Registration message was created')
        return json_data

    def unregister_msg(self):
        data = {}
        data['type'] = 'UNREGISTER'
        data['from'] = str(self.conf_manager.get('REGISTRATION', 'from'))
        data['password'] = str(self.conf_manager.get('REGISTRATION', 'password'))
        data['macAddresses'] = str(self.conf_manager.get('REGISTRATION', 'macAddresses'))
        data['ipAddresses'] = str(self.conf_manager.get('REGISTRATION', 'ipAddresses'))
        data['hostname'] = str(self.conf_manager.get('REGISTRATION', 'hostname'))
        # data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Unregister message was created')
        return json_data
