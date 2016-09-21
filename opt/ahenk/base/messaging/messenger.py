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


class Messenger(ClientXMPP):
    def __init__(self):
        scope = Scope().get_instance()

        self.logger = scope.get_logger()
        self.configuration_manager = scope.get_configuration_manager()
        self.event_manger = scope.get_event_manager()
        self.execution_manager = scope.get_execution_manager()

        self.my_jid = str(
            self.configuration_manager.get('CONNECTION', 'uid') + '@' + self.configuration_manager.get('CONNECTION',
                                                                                                       'servicename'))
        self.my_pass = str(self.configuration_manager.get('CONNECTION', 'password'))

        ClientXMPP.__init__(self, self.my_jid, self.my_pass)

        self.auto_authorize = True
        self.auto_subscribe = True

        self.hostname = str(socket.gethostbyname(self.configuration_manager.get('CONNECTION', 'host')))
        self.receiver_resource = self.configuration_manager.get('CONNECTION', 'receiverresource')

        if self.configuration_manager.get('CONNECTION', 'use_tls').strip().lower() == 'true':
            self.use_tls = True
        else:
            self.use_tls = False

        self.receiver = self.configuration_manager.get('CONNECTION',
                                                       'receiverjid') + '@' + self.configuration_manager.get(
            'CONNECTION', 'servicename')

        if self.receiver_resource:
            self.receiver += '/' + self.receiver_resource

        self.logger.debug('XMPP Messager parameters were set')

        self.register_extensions()
        self.add_listeners()

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030')  # Service Discovery
            self.register_plugin('xep_0199')  # XMPP Ping

            self.logger.debug('[Messenger]Extension were registered: xep_0030,xep_0199')
            return True
        except Exception as e:
            self.logger.error('[Messenger]Extension registration is failed! Error Message: {0}'.format(str(e)))
            return False

    def add_listeners(self):
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('session_end', self.session_end)
        self.add_event_handler('message', self.recv_direct_message)

        self.logger.debug('Event handlers were added')

    def connect_to_server(self):  # Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self['feature_mechanisms'].unencrypted_plain = True

            self.connect((self.hostname, 5222), use_tls=self.use_tls)
            self.process(block=False)
            self.logger.debug('Connection were established successfully')
            return True
        except Exception as e:
            self.logger.error('Connection to server is failed! Error Message: {0}'.format(str(e)))
            return False

    def session_end(self):
        self.logger.warning('DISCONNECTED')

    def session_start(self, event):
        self.logger.debug('Session was started')
        self.get_roster()
        self.send_presence()

    def send_direct_message(self, msg):
        try:
            self.logger.info('<<--------Sending message: {0}'.format(msg))
            self.send_message(mto=self.receiver, mbody=msg, mtype='normal')
        except Exception as e:
            self.logger.error(
                'A problem occurred while sending direct message. Error Message: {0}'.format(str(e)))

    def recv_direct_message(self, msg):
        if msg['type'] in ['normal']:
            self.logger.info('---------->Received message: {0}'.format(str(msg['body'])))
            try:
                j = json.loads(str(msg['body']))
                message_type = j['type']
                self.event_manger.fireEvent(message_type, str(msg['body']))
                self.logger.debug('Fired event is: {0}'.format(message_type))
            except Exception as e:
                self.logger.error(
                    'A problem occurred while keeping message. Error Message: {0}'.format(str(e)))
