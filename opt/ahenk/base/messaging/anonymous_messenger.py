#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json
import sys
import socket

from sleekxmpp import ClientXMPP
from base.scope import Scope

sys.path.append('../..')


class AnonymousMessenger(ClientXMPP):
    def __init__(self, message):
        # global scope of ahenk
        scope = Scope().get_instance()

        self.logger = scope.get_logger()
        self.configuration_manager = scope.get_configuration_manager()
        self.registration = scope.get_registration()
        self.event_manager = scope.get_event_manager()

        self.host = str(socket.gethostbyname(self.configuration_manager.get('CONNECTION', 'host')))
        self.service = str(self.configuration_manager.get('CONNECTION', 'servicename'))
        self.port = str(self.configuration_manager.get('CONNECTION', 'port'))

        ClientXMPP.__init__(self, self.service, None)

        self.message = message
        self.receiver_resource = self.configuration_manager.get('CONNECTION', 'receiverresource')
        self.receiver = self.configuration_manager.get('CONNECTION',
                                                       'receiverjid') + '@' + self.configuration_manager.get(
            'CONNECTION', 'servicename')
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
            self.logger.debug('Disconnecting...')
            self.disconnect()
            j = json.loads(str(msg['body']))
            message_type = j['type']
            self.event_manager.fireEvent(message_type, str(msg['body']))

    def send_direct_message(self, msg):
        self.logger.debug('<<--------Sending message: {0}'.format(msg))
        self.send_message(mto=self.receiver, mbody=msg, mtype='normal')
