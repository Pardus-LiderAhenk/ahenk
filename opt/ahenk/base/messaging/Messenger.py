#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json
import sys

from sleekxmpp import ClientXMPP

from base.Scope import Scope

sys.path.append('../..')


class Messenger(ClientXMPP):
    def __init__(self):
        scope = Scope().getInstance()

        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()
        self.event_manger = scope.getEventManager()
        self.execution_manager = scope.getExecutionManager()

        self.my_jid = str(self.configuration_manager.get('CONNECTION', 'uid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename'))
        self.my_pass = str(self.configuration_manager.get('CONNECTION', 'password'))

        ClientXMPP.__init__(self, self.my_jid, self.my_pass)

        self.hostname = self.configuration_manager.get('CONNECTION', 'host')
        self.resource_name = self.configuration_manager.get('CONNECTION', 'receiverresource')
        self.receiver = self.configuration_manager.get('CONNECTION', 'receiverjid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename') + '/' + self.resource_name
        self.receive_file_path = self.configuration_manager.get('CONNECTION', 'receivefileparam')
        self.logger.debug('[Messenger] XMPP Messager parameters were set')

        self.register_extensions()
        self.add_listeners()

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030')  # Service Discovery
            self.register_plugin('xep_0199')  # XMPP Ping

            self.logger.debug('[Messenger]Extension were registered: xep_0030,xep_0199')
            return True
        except Exception as e:
            self.logger.error('[Messenger]Extension registration is failed! Error Message: {}'.format(str(e)))
            return False

    def add_listeners(self):
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('session_end', self.session_end)
        self.add_event_handler('message', self.recv_direct_message)

        self.logger.debug('[Messenger] Event handlers were added')

    def connect_to_server(self):  # Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self['feature_mechanisms'].unencrypted_plain = True
            self.connect((self.hostname, 5222), use_tls=False)
            self.process(block=False)
            self.logger.debug('[Messenger] Connection were established successfully')
            return True
        except Exception as e:
            self.logger.error('[Messenger] Connection to server is failed! Error Message: {}'.format(str(e)))
            return False

    def session_end(self):
        print("disconnect")

    def session_start(self, event):
        self.logger.debug('[Messenger] Session was started')
        self.get_roster()
        self.send_presence()

    def send_direct_message(self, msg):
        try:
            self.logger.debug('[Messenger] <<--------Sending message: {}'.format(msg))
            self.send_message(mto=self.receiver, mbody=msg, mtype='normal')
        except Exception as e:
            self.logger.debug('[Messenger] A problem occurred while sending direct message. Error Message: {}'.format(str(e)))

    def recv_direct_message(self, msg):
        if msg['type'] in ('normal'):
            self.logger.debug('[Messenger] ---------->Received message: {}'.format(str(msg['body'])))
            try:
                j = json.loads(str(msg['body']))
                message_type = j['type']
                self.event_manger.fireEvent(message_type, str(msg['body']))
                self.logger.debug('[Messenger] Fired event is: {}'.format(message_type))

            except Exception as e:
                self.logger.debug('[Messenger] A problem occurred while keeping message. Error Message: {}'.format(str(e)))
