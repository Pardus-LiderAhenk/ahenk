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

        self.my_jid=self.get_jid_id()
        self.my_pass=self.get_password()

        slixmpp.ClientXMPP.__init__(self, self.my_jid,self.my_pass)
        #slixmpp.ClientXMPP.__init__(self,'volkan@localhost','volkan')

        self.message=None
        self.file=None
        self.room=None
        self.receiver=self.configurationManager.get('CONNECTION', 'receiverjid')+'@'+self.configurationManager.get('CONNECTION', 'host')+'/Smack'
        self.nick = self.configurationManager.get('CONNECTION', 'nick')
        self.receivefile=self.configurationManager.get('CONNECTION', 'receiveFileParam')

        if file_path is not None and file_path!='':
            self.file=open(file_path, 'rb')
            print('file path-'+file_path+"-"+self.my_jid+"-"+self.my_pass)
        if message is not None and message!='':
            self.message=message

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.recv_direct_message)
        self.add_event_handler("socks5_connected", self.stream_opened)
        self.add_event_handler("socks5_data", self.stream_data)
        self.add_event_handler("socks5_closed", self.stream_closed)

        self.register_extensions()


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
            self.registration.registration_reply=str(msg['body'])
            self.disconnect(wait=False)

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
        self.disconnect()


    @asyncio.coroutine
    def send_file(self,event):
        print("send file")
        try:
            # Open the S5B stream in which to write to.
            print("try")
            proxy = yield from self['xep_0065'].handshake(self.receiver)
            print("proxy")
            # Send the entire file.
            while True:
                data = self.file.read(1048576)
                if not data:
                    print("not data")
                    break
                yield from proxy.write(data)
            # And finally close the stream.
            print("while bitti")
            proxy.transport.write_eof()
        except (IqError, IqTimeout):
            print('File transfer errored')
        else:
            print('File transfer finished')
        finally:
            print("close")
            self.file.close()
            self.disconnect()

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

    def send_direct_message(self,msg):
        #need connection control
        self.send_message(mto=self.receiver,mbody=msg,mtype='chat')
        if self.configurationManager.get('CONNECTION', 'uid') != "" and  self.configurationManager.get('CONNECTION', 'uid') is not None:
            self.disconnect()

    def connect_to_server(self):# Connect to the XMPP server and start processing XMPP stanzas.
        try:
            print("connec")
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
