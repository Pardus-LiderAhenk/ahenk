#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json
import sys
import socket
from base.util.util import Util
import time
from base.system.system import System

import pwd

from helper import system as sysx

from sleekxmpp import ClientXMPP
from base.scope import Scope

sys.path.append('../..')


class AnonymousMessenger(ClientXMPP):
    def __init__(self, message, host= None, servicename= None):
        # global scope of ahenk
        scope = Scope().get_instance()

        self.logger = scope.get_logger()
        self.configuration_manager = scope.get_configuration_manager()
        self.registration = scope.get_registration()
        self.event_manager = scope.get_event_manager()

        if host is not None and servicename is not None:
            self.host = str(host)
            self.service = str(servicename)
            self.port = str(self.configuration_manager.get('CONNECTION', 'port'))

        # self.host = str(socket.gethostbyname(self.configuration_manager.get('CONNECTION', 'host')))
        # self.service = str(self.configuration_manager.get('CONNECTION', 'servicename'))
        # self.port = str(self.configuration_manager.get('CONNECTION', 'port'))

        ClientXMPP.__init__(self, self.service, None)

        self.message = message
        self.receiver_resource = self.configuration_manager.get('CONNECTION', 'receiverresource')
        self.receiver = self.configuration_manager.get('CONNECTION','receiverjid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename')
        if self.receiver_resource:
            self.receiver += '/' + self.receiver_resource

        if self.configuration_manager.get('CONNECTION', 'use_tls').strip().lower() == 'true':
            self.use_tls = True
        else:
            self.use_tls = False

        self.logger.debug('XMPP Receiver parameters were set')

        self.add_listeners()
        self.register_extensions()

    def add_listeners(self):
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.recv_direct_message)
        self.logger.debug('Event handlers were added')

    def session_start(self, event):
        self.logger.debug('Session was started')
        self.get_roster()
        self.send_presence()

        if self.message is not None:
            self.send_direct_message(self.message)

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030')  # Service Discovery
            self.register_plugin('xep_0199')  # XMPP Ping

            self.logger.debug('Extension were registered: xep_0030,xep_0199')
            return True
        except Exception as e:
            self.logger.error('Extension registration is failed! Error Message: {0}'.format(str(e)))
            return False

    def connect_to_server(self):
        try:
            self.logger.debug('Connecting to server...')
            self['feature_mechanisms'].unencrypted_plain = True
            self.connect((self.host, self.port), use_tls=self.use_tls)
            self.process(block=True)
            self.logger.debug('Connection were established successfully')
            return True
        except Exception as e:
            self.logger.error('Connection to server is failed! Error Message: {0}'.format(str(e)))
            return False

    def recv_direct_message(self, msg):
        if msg['type'] in ['normal']:
            self.logger.debug('---------->Received message: {0}'.format(str(msg['body'])))
            self.logger.debug('Reading registration reply')
            j = json.loads(str(msg['body']))
            message_type = j['type']
            status = str(j['status']).lower()
            dn = str(j['agentDn'])
            self.logger.debug('Registration status: ' + str(status))

            if 'not_authorized' == str(status):
                self.logger.info('Registration is failed. User not authorized')
                Util.show_message('Ahenk etki alanına alınamadı !! Sadece yetkili kullanıcılar etki alanına kayıt yapabilir.', 'Kullanıcı Yetkilendirme Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()

            elif 'already_exists' == str(status) or 'registered' == str(status) or 'registered_without_ldap' == str(status):
                try:
                    self.logger.info('Registred from server. Registration process starting.')
                    self.event_manager.fireEvent('REGISTRATION_SUCCESS', j)
                    msg = str(self.host) + " Etki Alanına hoş geldiniz."
                    Util.show_message(msg, "")
                    msg = "Değişikliklerin etkili olması için sistem yeniden başlayacaktır. Sistem yeniden başlatılıyor...."
                    Util.show_message(msg, "")
                    time.sleep(5)
                    self.logger.info('Disconnecting...')
                    self.disconnect()
                    self.logger.info('Rebooting...')
                    self.disable_local_users()
                    Util.shutdown();
                    System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
                    sys.exit(2)


                except Exception as e:
                    self.logger.error('Error Message: {0}.'.format(str(e)))
                    Util.show_message(str(e))
                    self.logger.debug('Disconnecting...')
                    self.disconnect()


            elif 'registration_error' == str(status):
                self.logger.info('Registration is failed. New registration request will send')
                #self.event_manager.fireEvent('REGISTRATION_ERROR', str(j))
                Util.show_message('Ahenk etki alanına alınamadı !! Kayıt esnasında hata oluştu. Lütfen sistem yöneticinize başvurunuz.',
                       'Sistem Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()
            else:
                self.event_manger.fireEvent(message_type, str(msg['body']))
                self.logger.debug('Fired event is: {0}'.format(message_type))

    def send_direct_message(self, msg):
        self.logger.debug('<<--------Sending message: {0}'.format(msg))
        self.send_message(mto=self.receiver, mbody=msg, mtype='normal')


    def disable_local_users(self):
        passwd_cmd = 'passwd -l {}'
        change_home = 'usermod -m -d {0} {1}'
        change_username = 'usermod -l {0} {1}'
        content = Util.read_file('/etc/passwd')
        kill_all_process = 'killall -KILL -u {}'
        for p in pwd.getpwall():
            self.logger.info("User: '{0}' will be disabled and changed username and home directory of username".format(p.pw_name))
            if not sysx.shell_is_interactive(p.pw_shell):
                continue
            if p.pw_uid == 0:
                continue
            if p.pw_name in content:
                new_home_dir = p.pw_dir.rstrip('/') + '-local/'
                new_username = p.pw_name+'-local'
                Util.execute(kill_all_process.format(p.pw_name))
                Util.execute(passwd_cmd.format(p.pw_name))
                Util.execute(change_username.format(new_username, p.pw_name))
                Util.execute(change_home.format(new_home_dir, new_username))
