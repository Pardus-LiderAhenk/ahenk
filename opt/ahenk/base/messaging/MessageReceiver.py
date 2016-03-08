#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import sys
sys.path.append('../..')
import slixmpp
import asyncio
import threading
import json
from threading import Thread
from multiprocessing import Process
from slixmpp.exceptions import IqError, IqTimeout
from base.Scope import Scope


class MessageReceiver(slixmpp.ClientXMPP):

    def __init__(self):

        # global scope of ahenk
        scope = Scope().getInstance()

        # configuration_manager and logger comes from ahenk deamon
        self.logger = scope.getLogger()
        self.configurationManager = scope.getConfigurationManager()
        self.event_manger=scope.getEventManager()

        self.my_jid=self.get_jid_id()
        self.my_pass=self.get_password()

        slixmpp.ClientXMPP.__init__(self, self.my_jid,self.my_pass)

        self.room=None
        self.receiver=self.configurationManager.get('CONNECTION', 'receiverjid')+'@'+self.configurationManager.get('CONNECTION', 'host')+'/Smack'
        self.nick = self.configurationManager.get('CONNECTION', 'nick')
        self.receive_file_path=self.configurationManager.get('CONNECTION', 'receiveFileParam')

        #TODO get default folder path from receivefile
        #self.file = open('/home/volkan/Desktop/yaz.txt', 'rb')

        self.register_extensions()
        self.add_listeners()
        self.connect()

    def get_jid_id(self):
        if self.configurationManager.get('CONNECTION', 'uid') == "" or  self.configurationManager.get('CONNECTION', 'uid') is None:
            return str(self.configurationManager.get('CONNECTION', 'host')) #is user want to create connection as anonymous
        else:
            return str(self.configurationManager.get('CONNECTION', 'uid')+'@'+self.configurationManager.get('CONNECTION', 'host')+'/1793816026658382528511590341137904818696727194330755982493')

    def get_password(self):
        if self.configurationManager.get('CONNECTION', 'password') == "" or  self.configurationManager.get('CONNECTION', 'password') is None:
            return None
        else:
            return str(self.configurationManager.get('CONNECTION', 'password'))

    def add_listeners(self):
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.recv_direct_message)
        self.add_event_handler("socks5_connected", self.stream_opened)
        self.add_event_handler("socks5_data", self.stream_data)
        self.add_event_handler("socks5_closed", self.stream_closed)

        self.add_event_handler("ibb_stream_start", self.stream_opened)
        self.add_event_handler("ibb_stream_data", self.stream_data)
        self.add_event_handler("ibb_stream_end", self.stream_closed)

    def stream_opened(self, sid):
        print('stream opened')
        #self.logger.info('Stream opened. %s', sid)
        self.file = open(self.receive_file_path+self.stream_id, 'wb')
        return self.file

    def stream_data(self, data):
        print('stream data')
        #self.logger.info('Stream data.')
        self.file.write(data)

    def stream_closed(self, exception):
        print('stream close')
        #self.logger.info('Stream closed. %s', exception)
        self.file.close()

    def session_start(self, event):
        self.get_roster()
        self.send_presence()


    def invite_auto_accept(self, inv):
        self.room=inv['from']
        print("(%s) invite is accepted" % str(self.room))
        self.plugin['xep_0045'].joinMUC(self.room,self.nick,wait=True)
        self.send_message(mto=self.room.bare,mbody="Hi all!",mtype='groupchat')
        return self.room

    def recv_muc_message(self, msg):#auto reply

        if msg['mucnick'] != self.nick:
            print("%s : %s" % (str(msg['from']),str(msg['body'])) )
            self.send_message(mto=msg['from'].bare,mbody="I got it, %s." % msg['mucnick'],mtype='groupchat')
        else:
            print("%s : %s" % (str(msg['mucnick']),str(msg['body'])))

    def recv_direct_message(self, msg): #TODO burada mesajın type ını event olarak fırlat
        if msg['type'] in ('chat', 'normal'):
            j = json.loads(str(msg['body']))
            type =j['type']
            print ("event will be fired:"+type)
            self.event_manger.fireEvent(type,str(msg['body']))


    def connect_to_server(self):# Connect to the XMPP server and start processing XMPP stanzas.
        try:

            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.process())

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
            self.register_plugin('xep_0065', {'auto_accept': True}) # SOCKS5 Bytestreams
            self.register_plugin('xep_0047', {'auto_accept': True}) # In-band Bytestreams

            #self.logger.info('Extension were registered: xep_0030,xep_0045,xep_0199,xep_0065')
            return True
        except Exception as e:
            #self.logger.error('Extension registration is failed!(%s)\n' % (e.errno, e.strerror))
            return False
