#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json, os, asyncio, slixmpp, sys
sys.path.append('../..')
from base.Scope import Scope



class MessageReceiver(slixmpp.ClientXMPP):

    def __init__(self):
        # global scope of ahenk
        scope = Scope().getInstance()

        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()
        self.event_manger=scope.getEventManager()
        self.execution_manager=scope.getExecutionManager()

        self.my_jid=self.get_jid_id()
        self.my_pass=self.get_password()

        slixmpp.ClientXMPP.__init__(self, self.my_jid,self.my_pass)

        self.room=None
        self.receiver=self.configuration_manager.get('CONNECTION', 'receiverjid')+'@'+self.configuration_manager.get('CONNECTION', 'host')+'/Smack'
        self.nick = self.configuration_manager.get('CONNECTION', 'nick')
        self.receive_file_path=self.configuration_manager.get('CONNECTION', 'receiveFileParam')
        self.logger.debug('[MessageReceiver] XMPP Receiver parameters were set')

        self.register_extensions()
        self.add_listeners()
        self.connect()

    def get_jid_id(self):
        if self.configuration_manager.get('CONNECTION', 'uid') == "" or  self.configuration_manager.get('CONNECTION', 'uid') is None:
            self.logger.debug('[MessageReceiver] Parameters were set as anonymous account')
            return str(self.configuration_manager.get('CONNECTION', 'host'))
        else:
            self.logger.debug('[MessageReceiver] Parameters were set as defined account')
            return str(self.configuration_manager.get('CONNECTION', 'uid')+'@'+self.configuration_manager.get('CONNECTION', 'host')+'/receiver')

    def get_password(self):
        if self.configuration_manager.get('CONNECTION', 'password') == "" or  self.configuration_manager.get('CONNECTION', 'password') is None:
            return None
        else:
            return str(self.configuration_manager.get('CONNECTION', 'password'))

    def add_listeners(self):
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.recv_direct_message)

        self.add_event_handler("socks5_connected", self.stream_opened)
        self.add_event_handler("socks5_data", self.stream_data)
        self.add_event_handler("socks5_closed", self.stream_closed)

        self.add_event_handler("ibb_stream_start", self.stream_opened)
        self.add_event_handler("ibb_stream_data", self.stream_data)
        self.add_event_handler("ibb_stream_end", self.stream_closed)

        self.logger.debug('[MessageReceiver] Event handlers were added')

    def stream_opened(self, sid):
        self.logger.debug('[MessageReceiver] Stream was opened. Stream id: '+str(self.stream_id))
        self.file = open(self.receive_file_path+self.stream_id, 'wb')
        return self.file

    def stream_data(self, data):
        self.logger.debug('[MessageReceiver] Receiving file...')
        self.file.write(data)

    def stream_closed(self, exception):
        self.logger.debug('[MessageReceiver] Stream was closed')
        self.file.close()
        self.set_file_name_to_md5()

    def session_start(self, event):
        self.logger.debug('[MessageReceiver] Session was started')
        self.get_roster()
        self.send_presence()

    def send_direct_message(self,msg):
        self.logger.debug('[MessageReceiver] Sending message: '+msg)
        self.send_message(mto=self.receiver,mbody=msg,mtype='normal')

    def invite_auto_accept(self, inv):
        self.room=inv['from']
        self.logger.debug('[MessageReceiver] (%s) invite is accepted' % str(self.room))
        self.plugin['xep_0045'].joinMUC(self.room,self.nick,wait=True)
        self.send_message(mto=self.room.bare,mbody="Hi all!",mtype='groupchat')
        return self.room

    def recv_muc_message(self, msg):
        if msg['mucnick'] != self.nick:
            self.logger.debug('[MessageReceiver] %s : %s' % (str(msg['from']),str(msg['body'])) )
            self.send_message(mto=msg['from'].bare,mbody="I got it, %s." % msg['mucnick'],mtype='groupchat')
        else:
            self.logger.debug('[MessageReceiver] %s : %s' % (str(msg['mucnick']),str(msg['body'])))

    def recv_direct_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            j = json.loads(str(msg['body']))
            type =j['type']
            self.logger.debug('[MessageReceiver] Fired event is: '+type)
            self.event_manger.fireEvent(type,str(msg['body']).lower())

    def connect_to_server(self):# Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self.logger.debug('[MessageReceiver] Connecting to server as thread')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.process())
            self.logger.debug('[MessageReceiver] Connection were established successfully')
            return True
        except Exception as e:
            self.logger.error('[MessageReceiver] Connection to server is failed! '+e)
            return False

    def set_file_name_to_md5(self):
        self.logger.debug('[MessageReceiver] Renaming file as md5 hash')
        md5_hash=self.execution_manager.get_md5_file(self.file.name)
        os.rename(self.file.name,self.receive_file_path+md5_hash)

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030') # Service Discovery
            self.register_plugin('xep_0045') # Multi-User Chat
            self.register_plugin('xep_0199') # XMPP Ping
            self.register_plugin('xep_0065', {'auto_accept': True}) # SOCKS5 Bytestreams
            self.register_plugin('xep_0047', {'auto_accept': True}) # In-band Bytestreams

            self.logger.debug('Extension were registered: xep_0030,xep_0045,xep_0199,xep_0065,xep_0047')
            return True
        except Exception as e:
            self.logger.error('Extension registration is failed!(%s)\n' % (e.errno, e.strerror))
            return False
