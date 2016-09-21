#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import json

from base.scope import Scope
from base.system.system import System
from base.util.util import Util


# TODO Message Factory
class Messaging(object):
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.conf_manager = scope.get_configuration_manager()
        self.db_service = scope.get_db_service()
        self.event_manger = scope.get_event_manager()

    def missing_plugin_message(self, plugin):
        data = dict()
        data['type'] = 'MISSING_PLUGIN'
        data['pluginName'] = plugin.get_name()
        data['pluginVersion'] = plugin.get_version()

        json_data = json.dumps(data)
        self.logger.debug('Missing plugin message was created')
        return str(json_data)

    def task_status_msg(self, response):
        data = dict()
        data['type'] = response.get_type()
        data['taskId'] = response.get_id()
        data['responseCode'] = response.get_code()
        data['responseMessage'] = response.get_message()
        response_data = None
        if response.get_data() is not None:
            response_data = json.loads(str(response.get_data()))
        data['responseData'] = response_data
        data['contentType'] = response.get_content_type()
        data['timestamp'] = response.get_timestamp()

        json_data = json.dumps(data)
        self.logger.debug('Task status message was created')
        return str(json_data)

    def policy_status_msg(self, response):
        data = dict()
        data['type'] = response.get_type()
        data['policyVersion'] = response.get_policy_version()
        data['commandExecutionId'] = response.get_execution_id()
        data['responseCode'] = response.get_code()
        data['responseMessage'] = response.get_message()

        response_data = None
        if response.get_data() is not None:
            response_data = json.loads(str(response.get_data()))

        data['responseData'] = response_data
        data['contentType'] = response.get_content_type()
        data['timestamp'] = response.get_timestamp()

        json_data = json.dumps(data)
        self.logger.debug('Policy status message was created')
        return str(json_data)

    def login_msg(self, username):
        data = dict()
        data['type'] = 'LOGIN'
        data['username'] = username
        data['ipAddresses'] = str(System.Hardware.Network.ip_addresses()).replace('[', '').replace(']', '')
        data['timestamp'] = Util.timestamp()
        json_data = json.dumps(data)
        self.logger.debug('Login message was created')
        return json_data

    def logout_msg(self, username):
        data = dict()
        data['type'] = 'LOGOUT'
        data['username'] = str(username)
        data['timestamp'] = Util.timestamp()
        json_data = json.dumps(data)
        self.logger.debug('Logout message was created')
        return json_data

    def policy_request_msg(self, username):
        data = dict()
        data['type'] = 'GET_POLICIES'

        user_policy_number = self.db_service.select_one_result('policy', 'version',
                                                               'type = \'U\' and name = \'' + username + '\'')
        machine_policy_number = self.db_service.select_one_result('policy', 'version', 'type = \'A\'')

        data['userPolicyVersion'] = user_policy_number
        data['agentPolicyVersion'] = machine_policy_number

        data['username'] = str(username)
        data['timestamp'] = Util.timestamp()
        json_data = json.dumps(data)
        self.logger.debug('Get Policies message was created')
        return json_data

    def registration_msg(self):
        data = dict()
        data['type'] = 'REGISTER'
        data['from'] = self.db_service.select_one_result('registration', 'jid', ' 1=1')
        data['password'] = self.db_service.select_one_result('registration', 'password', ' 1=1')

        params = self.db_service.select_one_result('registration', 'params', ' 1=1')
        data['data'] = json.loads(str(params))
        json_params = json.loads(str(params))
        data['macAddresses'] = json_params['macAddresses']
        data['ipAddresses'] = json_params['ipAddresses']
        data['hostname'] = json_params['hostname']

        data['timestamp'] = self.db_service.select_one_result('registration', 'timestamp', ' 1=1')
        json_data = json.dumps(data)
        self.logger.debug('Registration message was created')
        return json_data

    def ldap_registration_msg(self):
        data = dict()
        data['type'] = 'REGISTER_LDAP'
        data['from'] = str(self.conf_manager.get('REGISTRATION', 'from'))
        data['password'] = str(self.conf_manager.get('REGISTRATION', 'password'))
        data['macAddresses'] = str(self.conf_manager.get('REGISTRATION', 'macAddresses'))
        data['ipAddresses'] = str(self.conf_manager.get('REGISTRATION', 'ipAddresses'))
        data['hostname'] = str(self.conf_manager.get('REGISTRATION', 'hostname'))
        data['timestamp'] = Util.timestamp()
        json_data = json.dumps(data)
        self.logger.debug('LDAP Registration message was created')
        return json_data

    def unregister_msg(self):
        data = dict()
        data['type'] = 'UNREGISTER'
        data['from'] = str(self.conf_manager.get('REGISTRATION', 'from'))
        data['password'] = str(self.conf_manager.get('REGISTRATION', 'password'))
        data['macAddresses'] = str(self.conf_manager.get('REGISTRATION', 'macAddresses'))
        data['ipAddresses'] = str(self.conf_manager.get('REGISTRATION', 'ipAddresses'))
        data['hostname'] = str(self.conf_manager.get('REGISTRATION', 'hostname'))
        # data['username'] = str(pwd.getpwuid( os.getuid() )[ 0 ])
        data['timestamp'] = Util.timestamp()
        json_data = json.dumps(data)
        self.logger.debug('Unregister message was created')
        return json_data

    def agreement_request_msg(self):
        data = dict()
        data['type'] = 'REQUEST_AGREEMENT'

        """
        contract_content = self.db_service.select_one_result('contract', 'content', 'id =(select MAX(id) from contract)')
        if contract_content is not None and contract_content != '':
            data['md5'] = Util.get_md5_text(contract_content)
        else:
            data['md5'] = ''
        """

        data['timestamp'] = Util.timestamp()
        json_data = json.dumps(data)
        self.logger.debug('Agreement request message was created')
        return json_data

    def agreement_answer_msg(self, username, answer):
        data = dict()
        data['type'] = 'AGREEMENT_STATUS'
        data['username'] = username
        data['accepted'] = answer
        data['timestamp'] = Util.timestamp()
        contract_content = self.db_service.select_one_result('contract', 'content',
                                                             'id =(select MAX(id) from contract)')
        if contract_content is not None and contract_content != '':
            data['md5'] = Util.get_md5_text(contract_content)
        else:
            data['md5'] = ''

        json_data = json.dumps(data)
        self.logger.debug('Agreement answer message was created')
        return json_data
