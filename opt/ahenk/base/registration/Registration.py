#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime
import json
import uuid
from uuid import getnode as get_mac

from base.Scope import Scope
from base.messaging.AnonymousMessager import AnonymousMessager
from base.system.system import System


class Registration():
    def __init__(self):
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.message_manager = scope.getMessageManager()
        self.event_manager = scope.getEventManager()
        self.messager = scope.getMessager()
        self.conf_manager = scope.getConfigurationManager()
        self.db_service = scope.getDbService()

        self.event_manager.register_event('REGISTRATION_RESPONSE', self.registration_process)

        if self.is_registered():
            self.logger.debug('[Registration] Ahenk already registered')
        else:
            self.register(True)

    def registration_request(self):
        self.logger.debug('[Registration] Requesting registration')
        anon_messager = AnonymousMessager(self.message_manager.registration_msg(), None)
        anon_messager.connect_to_server()

    def ldap_registration_request(self):
        self.logger.debug('[Registration] Requesting LDAP registration')
        self.messager.send_Direct_message(self.message_manager.ldap_registration_msg())

    def registration_process(self, reg_reply):
        self.logger.debug('[Registration] Reading registration reply')
        j = json.loads(reg_reply)
        self.logger.debug('[Registration]' + j['message'])
        status = str(j['status']).lower()
        dn = str(j['agentDn']).lower()

        self.logger.debug('[Registration] Registration status: ' + str(status))

        if 'already_exists' == str(status) or 'registered' == str(status) or 'registered_without_ldap' == str(status):
            self.logger.debug('dn:' + dn)
            self.update_registration_attrs(dn)
        elif 'registration_error' == str(status):
            self.logger.info('[Registration] Registration is failed. New registration request will send')
            self.re_register()
        else:
            self.logger.error('[Registration] Bad message type of registration response ')

    def update_registration_attrs(self, dn=None):
        self.logger.debug('[Registration] Registration configuration is updating...')
        self.db_service.update('registration', ['dn', 'registered'], [dn, 1], ' registered = 0')

        if self.conf_manager.has_section('CONNECTION'):
            self.conf_manager.set('CONNECTION', 'uid', self.db_service.select_one_result('registration', 'jid', ' registered=1'))
            self.conf_manager.set('CONNECTION', 'password', self.db_service.select_one_result('registration', 'password', ' registered=1'))
            # TODO  get file path?
            with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                self.conf_manager.write(configfile)
            self.logger.debug('[Registration] Registration configuration file is updated')

    def is_registered(self):
        registered = self.db_service.select_one_result('registration', 'registered', 'registered = 1')
        if registered == 1:
            return True
        else:
            return False

    def is_ldap_registered(self):
        dn = self.db_service.select_one_result('registration', 'dn', 'registered = 1')
        if dn is not None and dn != '':
            return True
        else:
            return False

    def register(self, uuid_depend_mac=False):

        cols = ['jid', 'password', 'registered', 'params', 'timestamp']
        vals = [str(self.generate_uuid(uuid_depend_mac)), str(self.generate_password()), 0, str(self.get_registration_params()), str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))]

        self.db_service.delete('registration', ' 1==1 ')
        self.db_service.update('registration', cols, vals)
        self.logger.debug('[Registration] Registration parameters were created')

    def get_registration_params(self):

        params = {
            'ipAddresses': str(System.Hardware.Network.ip_addresses()).replace('[', '').replace(']', ''),
            'macAddresses': str(System.Hardware.Network.mac_addresses()).replace('[', '').replace(']', ''),
            'hostname': System.Os.hostname(),
            'os.name': System.Os.name(),
            'os.version': System.Os.version(),
            'os.kernel': System.Os.kernel_release(),
            'os.distributionName': System.Os.distribution_name(),
            'os.distributionId': System.Os.distribution_id(),
            'os.distributionVersion': System.Os.distribution_version(),
            'os.architecture': System.Os.architecture(),
            'hardware.cpu.architecture': System.Hardware.Cpu.architecture(),
            'hardware.cpu.logicalCoreCount': System.Hardware.Cpu.logical_core_count(),
            'hardware.cpu.physicalCoreCount': System.Hardware.Cpu.physical_core_count(),
            'hardware.disk.total': System.Hardware.Disk.total(),
            'hardware.disk.used': System.Hardware.Disk.used(),
            'hardware.disk.free': System.Hardware.Disk.free(),
            'hardware.disk.partitions': System.Hardware.Disk.partitions(),
            'hardware.memory.total': System.Hardware.Memory.total(),
            'hardware.network.ipAddresses': System.Hardware.Network.ip_addresses(),
            'sessions.userNames': System.Sessions.user_name(),
        }

        return json.dumps(params)

    def unregister(self):
        self.logger.debug('[Registration] Ahenk is unregistering...')
        self.db_service.delete('registration', ' 1==1 ')
        self.logger.debug('[Registration] Ahenk is unregistered')

    def re_register(self):
        self.logger.debug('[Registration] Reregistrating...')
        self.unregister()
        self.register(False)

    def generate_uuid(self, depend_mac=True):
        if depend_mac is False:
            self.logger.debug('[Registration] uuid creating randomly')
            return uuid.uuid4()  # make a random UUID
        else:
            self.logger.debug('[Registration] uuid creating according to mac address')
            return uuid.uuid3(uuid.NAMESPACE_DNS, str(get_mac()))  # make a UUID using an MD5 hash of a namespace UUID and a mac address

    def generate_password(self):
        return uuid.uuid4()
