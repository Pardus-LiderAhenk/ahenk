#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import datetime
import json
import sys

sys.path.append('../..')
from base.Scope import Scope


# TODO Message Factory
class Messaging(object):
    def __init__(self):
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.conf_manager = scope.getConfigurationManager()
        self.db_service = scope.getDbService()
        self.event_manger = scope.getEventManager()

    def response_msg(self, response):
        print("response message")
        data = {}
        data['type'] = response.get_type()
        data['id'] = response.get_id()
        data['responseCode'] = response.get_code()
        data['responseMessage'] = response.get_message()
        data['responseData'] = response.get_data()
        data['contentType'] = response.get_content_type()
        data['timestamp'] = response.get_timestamp()

        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Response message was created')
        return str(json_data)


    def login_msg(self, username):
        data = {}
        data['type'] = 'LOGIN'
        data['username'] = username
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Login message was created')
        return json_data

    def logout_msg(self, username):
        data = {}
        data['type'] = 'LOGOUT'
        data['username'] = str(username)
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Logout message was created')
        return json_data

    def policy_request_msg(self, username):
        data = {}
        data['type'] = 'GET_POLICIES'

        user_policy_number = self.db_service.select_one_result('policy', 'version', 'type = \'U\' and name = \'' + username + '\'')
        machine_policy_number = self.db_service.select_one_result('policy', 'version', 'type = \'A\'')

        data['userPolicyVersion'] = user_policy_number
        data['machinePolicyVersion'] = machine_policy_number

        data['username'] = str(username)
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
