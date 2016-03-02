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

"""
--fetch parameters of connection  from conf file
--connect xmpp
--send direct message
--receive direct message
--send muc message
--receive muc message
--listen to muc invites
--auto accept muc invites
--send auto reply to muc messages
--receive file (0065)
--send file (0065)

"""

class MessageSender(slixmpp.ClientXMPP):

    def __init__(self,message):

        # global scope of ahenk
        scope = Scope()
        scope = scope.getInstance()

        # logger comes from ahenk deamon
        #configurationManager comes from ahenk deamon
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        #set parameters
        #slixmpp.ClientXMPP.__init__(self, self.configurationManager.get('CONNECTION', 'jid'), self.configurationManager.get('Connection_Param', 'password'))

        slixmpp.ClientXMPP.__init__(self, "volkan@localhost", "volkan")
        self.receiver="caner@localhost"
        #slixmpp.ClientXMPP.__init__(self, "volkan@localhost", "volkan")
        #self.receiver="caner@localhost"
        """
        self.nick = self.configurationManager.get('CONNECTION', 'nick')
        self.receiver=self.configurationManager.get('CONNECTION','receiverJid')
        self.sendfile=open(self.configurationManager.get('CONNECTION','sendFilePath'), 'rb')
        self.receivefile=self.configurationManager.get('CONNECTION', 'receiveFileParam')
        self.logger.info('Parameters were established')
        """
        self.room=None
        self.message=message

        self.add_event_handler("session_start", self.session_start)
        self.register_extensions()

        #!!! you have to use modified slixmpp for file transfering
        #self.send_file()

    def session_start(self, event):
        self.get_roster()
        self.send_presence()
        self.send_direct_message(self.message)

    def stream_opened(self, sid):
        #self.logger.info('Stream opened. %s', sid)
        return open(self.receivefile, 'wb')

    def stream_data(self, data):
        #self.logger.info('Stream data.')
        self.file.write(data)

    def stream_closed(self, exception):
        #self.logger.info('Stream closed. %s', exception)
        self.file.close()
        #self.disconnect()


    def send_file(self):
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

    def send_direct_message(self,msg):
        #need connection control
        self.send_message(mto=self.receiver,mbody=msg,mtype='chat')
        self.disconnect()

    def connect_to_server(self):# Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self.connect()
            self.process()
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
