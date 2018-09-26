#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime
import json
import uuid
from uuid import getnode as get_mac

from base.scope import Scope
from base.messaging.anonymous_messenger import AnonymousMessenger
from base.system.system import System
from base.timer.setup_timer import SetupTimer
from base.timer.timer import Timer
from base.util.util import Util
from helper import system as sysx
import pwd
import os, signal


class Registration:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.message_manager = scope.get_message_manager()
        self.event_manager = scope.get_event_manager()
        self.messenger = scope.get_messenger()
        self.conf_manager = scope.get_configuration_manager()
        self.db_service = scope.get_db_service()
        self.util = Util()

        self.event_manager.register_event('REGISTRATION_RESPONSE', self.registration_process)

        if self.is_registered():
            self.logger.debug('Ahenk already registered')
        else:
            self.register(True)

    def registration_request(self):
        self.logger.debug('Requesting registration')
        SetupTimer.start(Timer(System.Ahenk.registration_timeout(), timeout_function=self.registration_timeout,
                               checker_func=self.is_registered, kwargs=None))
        anon_messenger = AnonymousMessenger(self.message_manager.registration_msg())
        anon_messenger.connect_to_server()

    def ldap_registration_request(self):
        self.logger.debug('Requesting LDAP registration')
        self.messenger.send_Direct_message(self.message_manager.ldap_registration_msg())

    def registration_process(self, reg_reply):
        self.logger.debug('Reading registration reply')
        j = json.loads(reg_reply)
        self.logger.debug('[Registration]' + j['message'])
        status = str(j['status']).lower()
        dn = str(j['agentDn'])

        self.logger.debug('Registration status: ' + str(status))

        if 'already_exists' == str(status) or 'registered' == str(status) or 'registered_without_ldap' == str(status):
            self.logger.debug('Current dn:' + dn)
            self.update_registration_attrs(dn)
        elif 'registration_error' == str(status):
            self.logger.info('Registration is failed. New registration request will send')
            self.re_register()
        else:
            self.logger.error('Bad message type of registration response ')

    def update_registration_attrs(self, dn=None):
        self.logger.debug('Registration configuration is updating...')
        self.db_service.update('registration', ['dn', 'registered'], [dn, 1], ' registered = 0')

        if self.conf_manager.has_section('CONNECTION'):
            self.conf_manager.set('CONNECTION', 'uid',
                                  self.db_service.select_one_result('registration', 'jid', ' registered=1'))
            self.conf_manager.set('CONNECTION', 'password',
                                  self.db_service.select_one_result('registration', 'password', ' registered=1'))
            # TODO  get file path?
            with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                self.conf_manager.write(configfile)
            self.logger.debug('Registration configuration file is updated')
            self.disable_local_users()

    def is_registered(self):

        try:
            if str(System.Ahenk.uid()):
                return True
            else:
                return False
        except:
            return False

    def is_ldap_registered(self):
        dn = self.db_service.select_one_result('registration', 'dn', 'registered = 1')
        if dn is not None and dn != '':
            return True
        else:
            return False

    def register(self, uuid_depend_mac=False):

        cols = ['jid', 'password', 'registered', 'params', 'timestamp']
        vals = [str(System.Os.hostname()), str(self.generate_password()), 0,
                str(self.get_registration_params()), str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))]

        self.db_service.delete('registration', ' 1==1 ')
        self.db_service.update('registration', cols, vals)
        self.logger.debug('Registration parameters were created')

    def get_registration_params(self):

        parts = []
        for part in System.Hardware.Disk.partitions():
            parts.append(part[0])

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
            'hardware.disk.partitions': str(parts),
            'hardware.monitors': str(System.Hardware.monitors()),
            'hardware.screens': str(System.Hardware.screens()),
            'hardware.usbDevices': str(System.Hardware.usb_devices()),
            'hardware.printers': str(System.Hardware.printers()),
            'hardware.systemDefinitions': str(System.Hardware.system_definitions()),
            'hardware.model.version': str(System.Hardware.machine_model()),
	    'hardware.memory.total': System.Hardware.Memory.total(),
            'hardware.network.ipAddresses': str(System.Hardware.Network.ip_addresses()),
            'sessions.userNames': str(System.Sessions.user_name()),
            'bios.releaseDate': System.BIOS.release_date()[1].replace('\n', '') if System.BIOS.release_date()[
                                                                                       0] == 0 else 'n/a',
            'bios.version': System.BIOS.version()[1].replace('\n', '') if System.BIOS.version()[0] == 0 else 'n/a',
            'bios.vendor': System.BIOS.vendor()[1].replace('\n', '') if System.BIOS.vendor()[0] == 0 else 'n/a',
            'hardware.baseboard.manufacturer': System.Hardware.BaseBoard.manufacturer()[1].replace('\n', '') if
            System.Hardware.BaseBoard.manufacturer()[0] == 0 else 'n/a',
            'hardware.baseboard.version': System.Hardware.BaseBoard.version()[1].replace('\n', '') if
            System.Hardware.BaseBoard.version()[0] == 0 else 'n/a',
            'hardware.baseboard.assetTag': System.Hardware.BaseBoard.asset_tag()[1].replace('\n', '') if
            System.Hardware.BaseBoard.asset_tag()[0] == 0 else 'n/a',
            'hardware.baseboard.productName': System.Hardware.BaseBoard.product_name()[1].replace('\n', '') if
            System.Hardware.BaseBoard.product_name()[0] == 0 else 'n/a',
            'hardware.baseboard.serialNumber': System.Hardware.BaseBoard.serial_number()[1].replace('\n', '') if
            System.Hardware.BaseBoard.serial_number()[0] == 0 else 'n/a',
        }

        return json.dumps(params)

    def unregister(self):
        self.logger.debug('Ahenk is unregistering...')
        self.db_service.delete('registration', ' 1==1 ')
        self.logger.debug('Ahenk is unregistered')

    def re_register(self):
        self.logger.debug('Reregistrating...')
        self.unregister()
        self.register(False)

    def generate_uuid(self, depend_mac=True):
        if depend_mac is False:
            self.logger.debug('uuid creating randomly')
            return uuid.uuid4()  # make a random UUID
        else:
            self.logger.debug('uuid creating according to mac address')
            return uuid.uuid3(uuid.NAMESPACE_DNS,
                              str(get_mac()))  # make a UUID using an MD5 hash of a namespace UUID and a mac address

    def generate_password(self):
        return uuid.uuid4()

    def registration_timeout(self):
        self.logger.error(
            'Could not reach registration response from Lider. Be sure XMPP server is reachable and it supports anonymous message, Lider is running properly '
            'and it is connected to XMPP server! Check your Ahenk configuration file (/etc/ahenk/ahenk.conf)')
        self.logger.error('Ahenk is shutting down...')
        print('Ahenk is shutting down...')
        System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))

    def disable_local_users(self):
        passwd_cmd = 'passwd -l {}'
        change_home = 'usermod -m -d {0} {1}'
        change_username = 'usermod -l {0} {1}'
        content = self.util.read_file('/etc/passwd')
        for p in pwd.getpwall():

            if not sysx.shell_is_interactive(p.pw_shell):
                continue
            if p.pw_uid == 0:
                continue
            if p.pw_name in content:

                new_home_dir = p.pw_dir.rstrip('/') + '-local/'
                new_username = p.pw_name+'-local'
                sysx.killuserprocs(p.pw_uid)
                self.util.execute(passwd_cmd.format(p.pw_name))
                self.util.execute(change_username.format(new_username, p.pw_name))
                self.util.execute(change_home.format(new_home_dir, new_username))
                self.logger.debug("User: '{0}' will be disabled and changed username and home directory of username".format(p.pw_name))
