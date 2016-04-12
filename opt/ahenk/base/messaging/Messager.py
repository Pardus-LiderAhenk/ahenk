#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import asyncio
import json
import os
import sys

import slixmpp

sys.path.append('../..')
from slixmpp.exceptions import IqError, IqTimeout
from base.Scope import Scope


class Messager(slixmpp.ClientXMPP):
    global loop

    def __init__(self):
        # global scope of ahenk
        scope = Scope().getInstance()

        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()
        self.event_manger = scope.getEventManager()
        self.execution_manager = scope.getExecutionManager()

        self.my_jid = str(self.configuration_manager.get('CONNECTION', 'uid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename') + '/receiver')
        self.my_pass = str(self.configuration_manager.get('CONNECTION', 'password'))

        slixmpp.ClientXMPP.__init__(self, self.my_jid, self.my_pass)

        self.file = None
        self.hostname = self.configuration_manager.get('CONNECTION', 'host')
        self.receiver = self.configuration_manager.get('CONNECTION', 'receiverjid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename') + '/Smack'
        self.nick = self.configuration_manager.get('CONNECTION', 'nick')
        self.receive_file_path = self.configuration_manager.get('CONNECTION', 'receiveFileParam')
        self.logger.debug('[Messager] XMPP Receiver parameters were set')

        self.register_extensions()
        self.add_listeners()

    def add_listeners(self):
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('session_end', self.session_end)
        self.add_event_handler('message', self.recv_direct_message)

        self.add_event_handler('socks5_connected', self.stream_opened)
        self.add_event_handler('socks5_data', self.stream_data)
        self.add_event_handler('socks5_closed', self.stream_closed)

        self.add_event_handler('ibb_stream_start', self.stream_opened)
        self.add_event_handler('ibb_stream_data', self.stream_data)
        self.add_event_handler('ibb_stream_end', self.stream_closed)

        self.logger.debug('[Messager] Event handlers were added')

    def stream_opened(self, sid):
        self.logger.debug('[Messager] Stream was opened. Stream id: ' + str(self.stream_id))
        self.file = open(self.receive_file_path + self.stream_id, 'wb')
        return self.file

    def stream_data(self, data):
        self.logger.debug('[Messager] Receiving file...')
        self.file.write(data)

    def stream_closed(self, exception):
        self.logger.debug('[Messager] Stream was closed')
        self.file.close()
        self.set_file_name_md5()

    def session_start(self, event):
        self.logger.debug('[Messager] Session was started')
        self.get_roster()
        self.send_presence()

    def session_end(self):
        print("disconnect")

    # TODO need check
    def send_file(self, file_path):
        self.file = open(file_path, 'rb')

        # TODO read conf file check file size if file size is bigger than max size, divide and send parts.after all send message about them
        self.logger.debug('[Messager] Sending file: ' + self.file.name)
        try:
            self.logger.debug('[Messager] Handshaking for file transfering...')
            # Open the S5B stream in which to write to.
            proxy = yield from self['xep_0065'].handshake(self.receiver)
            # Send the entire file.
            self.logger.debug('[Messager] Started to streaming file...')
            while True:
                data = self.file.read(1048576)
                if not data:
                    break
                yield from proxy.write(data)
            # And finally close the stream.
            proxy.transport.write_eof()
        except (IqError, IqTimeout):
            self.logger.error('[Messager] File transfer errored')
        else:
            self.logger.debug('[Messager] File transfer finished successfully')
        finally:
            self.file.close()

    def send_direct_message(self, msg):
        self.logger.debug('[Messager] Sending message: ' + msg)
        self.send_message(mto=self.receiver, mbody=msg, mtype='normal')
        print('<---' + msg)

    def recv_direct_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            j = json.loads(str(msg['body']))
            message_type = j['type']
            self.logger.debug('[Messager] Fired event is: ' + message_type)
            print('----->' + str(msg['body']))
            self.event_manger.fireEvent(message_type, str(msg['body']))

    def connect_to_server(self):  # Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self.logger.debug('[Messager] Connecting to server as thread')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.connect((self.hostname, 5222))
            self.process(forever=True)
            self.logger.debug('[Messager] Connection were established successfully')
            return True
        except Exception as e:
            self.logger.error('[Messager] Connection to server is failed! ' + e)
            return False

    def set_file_name_md5(self):
        self.logger.debug('[Messager] Renaming file as md5 hash')
        md5_hash = self.execution_manager.get_md5_file(self.file.name)
        os.rename(self.file.name, self.receive_file_path + md5_hash)

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030')  # Service Discovery
            self.register_plugin('xep_0045')  # Multi-User Chat
            self.register_plugin('xep_0199')  # XMPP Ping
            self.register_plugin('xep_0065', {'auto_accept': True})  # SOCKS5 Bytestreams
            self.register_plugin('xep_0047', {'auto_accept': True})  # In-band Bytestreams

            self.logger.debug('[Messager]Extension were registered: xep_0030,xep_0045,xep_0199,xep_0065,xep_0047')
            return True
        except Exception as e:
            self.logger.error('[Messager]Extension registration is failed!(%s)\n' % (e.errno, e.strerror))
            return False

    '''

    def invite_auto_accept(self, inv):
        self.room = inv['from']
        self.logger.debug('[Messager] (%s) invite is accepted' % str(self.room))
        self.plugin['xep_0045'].joinMUC(self.room, self.nick, wait=True)
        self.send_message(mto=self.room.bare, mbody='Hi all!', mtype='groupchat')
        return self.room

    def recv_muc_message(self, msg):
        if msg['mucnick'] != self.nick:
            self.logger.debug('[Messager] %s : %s' % (str(msg['from']), str(msg['body'])))
            self.send_message(mto=msg['from'].bare, mbody='I got it, %s.' % msg['mucnick'], mtype='groupchat')
        else:
            self.logger.debug('[Messager] %s : %s' % (str(msg['mucnick']), str(msg['body'])))

    '''
