#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import sys
sys.path.append('../..')
import slixmpp
import asyncio
import threading
from threading import Thread
from multiprocessing import Process
from slixmpp.exceptions import IqError, IqTimeout
from base.Scope import Scope

class MessageSender(slixmpp.ClientXMPP):

    def __init__(self,message,file_path):

        # global scope of ahenk
        scope = Scope().getInstance()

        # logger comes from ahenk deamon
        #configurationManager comes from ahenk deamon
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        self.registration=scope.getRegistration()
        self.event_manager = scope.getEventManager()

        self.my_jid=self.get_jid_id()
        self.my_pass=self.get_password()

        slixmpp.ClientXMPP.__init__(self, self.my_jid,self.my_pass)

        self.message=None
        self.file=None
        self.room=None
        self.receiver=self.configurationManager.get('CONNECTION', 'receiverjid')+'@'+self.configurationManager.get('CONNECTION', 'host')+'/Smack'
        self.nick = self.configurationManager.get('CONNECTION', 'nick')
        self.receivefile=self.configurationManager.get('CONNECTION', 'receiveFileParam')

        if file_path is not None and file_path!='':
            self.file=open(file_path, 'rb')
        if message is not None:
            self.message=message

        self.add_listeners()
        self.register_extensions()

    def add_listeners(self):
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.recv_direct_message)
        self.add_event_handler("socks5_connected", self.stream_opened)
        self.add_event_handler("socks5_data", self.stream_data)
        self.add_event_handler("socks5_closed", self.stream_closed)

    def get_jid_id(self):
        if self.configurationManager.get('CONNECTION', 'uid') == "" or  self.configurationManager.get('CONNECTION', 'uid') is None:
            return str(self.configurationManager.get('CONNECTION', 'host')) #is user want to create connection as anonymous
        else:
            return str(self.configurationManager.get('CONNECTION', 'uid')+'@'+self.configurationManager.get('CONNECTION', 'host'))

    def get_password(self):
        if self.configurationManager.get('CONNECTION', 'password') == "" or  self.configurationManager.get('CONNECTION', 'password') is None:
            return None
        else:
            return str(self.configurationManager.get('CONNECTION', 'password'))

    def recv_direct_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print ("%s : %s" % (msg['from'], msg['body']))
            self.disconnect()
            self.event_manager.fireEvent('confirm_registration',str(msg['body'])) #only anonymous account can fire confirm_registration


    @asyncio.coroutine
    def session_start(self, event):
        self.get_roster()
        self.send_presence()

        if self.message is not None:
            self.send_direct_message(self.message)

        if self.file is not None:
            try:
                # Open the S5B stream in which to write to.
                proxy = yield from self['xep_0065'].handshake(self.receiver)
                # Send the entire file.
                while True:
                    data = self.file.read(1048576)
                    if not data:
                        break
                    yield from proxy.write(data)
                # And finally close the stream.
                proxy.transport.write_eof()
            except (IqError, IqTimeout):
                print('File transfer errored')
            else:
                print('File transfer finished')
            finally:
                self.file.close()

        if (self.message is None and self.file is None) or self.get_password() is not None:
            self.disconnect()

    def stream_opened(self, sid):
        #self.logger.info('Stream opened. %s', sid)
        self.file = open(self.receive_file_path+self.stream_id, 'wb')
        return self.file

    def stream_data(self, data):
        #self.logger.info('Stream data.')
        self.file.write(data)

    def stream_closed(self, exception):
        #self.logger.info('Stream closed. %s', exception)
        self.file.close()
        self.disconnect()

    def send_direct_message(self,msg):
        #need connection control
        print("sending...\n"+msg)
        self.send_message(mto=self.receiver,mbody=msg,mtype='normal')

    def connect_to_server(self):# Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self.connect()
            self.process(forever=False)
            #self.logger.info('Connection were established successfully')
            return True
        except Exception as e:
            print('Connection to server is failed (%s)\n' % (e.strerror))
            #self.logger.error('Connection to server is failed! '+e)
            return False

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030') # Service Discovery
            self.register_plugin('xep_0045') # Multi-User Chat
            self.register_plugin('xep_0199') # XMPP Ping
            self.register_plugin('xep_0065') # SOCKS5 Bytestreams

            #self.logger.info('Extension were registered: xep_0030,xep_0045,xep_0199,xep_0065')
            return True
        except Exception as e:
            #self.logger.error('Extension registration is failed!(%s)\n' % (e.errno, e.strerror))
            return False
