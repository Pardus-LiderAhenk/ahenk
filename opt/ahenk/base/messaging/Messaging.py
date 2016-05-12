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

    def missing_plugin_message(self, plugin):
        data = {}
        data['type'] = 'MISSING_PLUGIN'
        data['pluginName'] = plugin.get_name()
        data['pluginVersion'] = plugin.get_version()

        json_data = json.dumps(data)
        self.logger.debug('[Messaging]Missing plugin message was created')
        return str(json_data)

    """
    def response_msg(self, response):
        print("response message")
        data = {}
        data['type'] = response.get_type()
        data['taskId'] = response.get_id()
        data['responseCode'] = response.get_code()
        data['responseMessage'] = response.get_message()
        data['responseData'] = response.get_data()
        data['contentType'] = response.get_content_type()
        data['timestamp'] = response.get_timestamp()

        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Response message was created')
        return str(json_data)
    """

    def task_status_msg(self, response):
        data = {}
        data['type'] = response.get_type()
        data['taskId'] = response.get_id()
        data['responseCode'] = response.get_code()
        data['responseMessage'] = response.get_message()
        data['responseData'] = response.get_data()
        data['contentType'] = response.get_content_type()
        data['timestamp'] = response.get_timestamp()

        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Task status message was created')
        return str(json_data)

    def policy_status_msg(self, response):
        data = {}
        data['type'] = response.get_type()
        data['policyVersion'] = response.get_policy_version()
        data['commandExecutionId'] = response.get_execution_id()
        data['responseCode'] = response.get_code()
        data['responseMessage'] = response.get_message()
        data['responseData'] = response.get_data()
        data['contentType'] = response.get_content_type()
        data['timestamp'] = response.get_timestamp()

        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Policy status message was created')
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
        data['agentPolicyVersion'] = machine_policy_number

        data['username'] = str(username)
        data['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
        json_data = json.dumps(data)
        self.logger.debug('[Messaging] Get Policies message was created')
        return json_data

    def registration_msg(self):
        data = {}
        data['type'] = 'REGISTER'
        data['from'] = self.db_service.select_one_result('registration', 'jid', ' 1=1')
        data['password'] = self.db_service.select_one_result('registration', 'password', ' 1=1')

        params = self.db_service.select_one_result('registration', 'params', ' 1=1')
        data['parameters'] = json.loads(str(params))
        json_params = json.loads(str(params))
        data['macAddresses'] = json_params['macAddresses']
        data['ipAddresses'] = json_params['ipAddresses']
        data['hostname'] = json_params['hostname']

        data['timestamp'] = self.db_service.select_one_result('registration', 'timestamp', ' 1=1')
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
