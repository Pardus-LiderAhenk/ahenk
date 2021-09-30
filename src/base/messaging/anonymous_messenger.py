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
import os

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

            self.logger.info('Reading registration reply')
            j = json.loads(str(msg['body']))
            message_type = j['type']
            status = str(j['status']).lower()
            dn = str(j['agentDn'])
            self.logger.debug('Registration status: ' + str(status))
            is_password = False
            for key, value in j.items():
                if "password" in key.lower():
                    j[key] = "********"
                    is_password = True
            if is_password:
                self.logger.info('---------->Received message: {0}'.format(str(j)))
            else:
                self.logger.info('---------->Received message: {0}'.format(str(msg['body'])))

            if 'not_authorized' == str(status):
                self.logger.debug('[REGISTRATION IS FAILED]. User not authorized')
                if self.registration.showUserNotify == True:
                    Util.show_message(os.getlogin(), ':0','Ahenk Lider MYS\`ye alınamadı !! Sadece yetkili kullanıcılar kayıt yapabilir.', 'Kullanıcı Yetkilendirme Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()
            elif 'registered' == str(status) or 'registered_without_ldap' == str(status):
                try:
                    self.logger.info('Registred from server. Registration process starting.')
                    self.event_manager.fireEvent('REGISTRATION_SUCCESS', j)
                    if self.registration.showUserNotify == True:
                        msg = str(self.host) + " Etki Alanına hoş geldiniz."
                        Util.show_message(os.getlogin(), ':0', msg, "UYARI")
                        msg = "Değişikliklerin etkili olması için sistem yeniden başlayacaktır. Sistem yeniden başlatılıyor...."
                        Util.show_message(os.getlogin(), ':0', msg, "UYARI")
                    time.sleep(3)
                    self.logger.info('Disconnecting...')
                    self.disconnect()
                    self.logger.info('Rebooting...')
                    #System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
                    #sys.exit(2)
                    Util.shutdown()

                except Exception as e:
                    self.logger.error('Error Message: {0}.'.format(str(e)))
                    if self.registration.showUserNotify == True:
                        Util.show_message(os.getlogin(), ':0',str(e))
                    self.logger.debug('Disconnecting...')
                    self.disconnect()
            elif 'already_exists' == str(status):
                self.logger.debug('[REGISTRATION IS FAILED] - Hostname already in use!')
                if self.registration.showUserNotify == True:
                    Util.show_message(os.getlogin(), ':0',
                                      '{0} bilgisayar adı zaten kullanılmaktadır. Lütfen bilgisayar adını değiştirerek tekrar deneyiniz'.format(System.Os.hostname()),
                                      'Bilgisayar İsimlendirme Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()

            elif 'registration_error' == str(status):
                self.logger.info('[REGISTRATION IS FAILED] - New registration request will send')
                #self.event_manager.fireEvent('REGISTRATION_ERROR', str(j))
                if self.registration.showUserNotify == True:
                    Util.show_message(os.getlogin(), ':0', 'Ahenk Lider MYS\`ye alınamadı !! Kayıt esnasında hata oluştu. Lütfen sistem yöneticinize başvurunuz.',
                       'Sistem Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()
            else:
                self.event_manager.fireEvent(message_type, str(msg['body']))
                self.logger.debug('Fired event is: {0}'.format(message_type))

    def send_direct_message(self, msg):
        body = json.loads(str(msg))
        if body['type'] == "REGISTER" or body['type'] == "UNREGISTER":
            is_password = False
            for key, value in body.items():
                if "password" in key.lower():
                    body[key] = "********"
                    is_password = True
            if is_password:
                self.logger.info('<<--------Sending message: {0}'.format(body))
        else:
            self.logger.info('<<--------Sending message: {0}'.format(msg))
        self.send_message(mto=self.receiver, mbody=msg, mtype='normal')
