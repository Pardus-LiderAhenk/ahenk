#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import slixmpp, asyncio, sys
sys.path.append('../..')
from slixmpp.exceptions import IqError, IqTimeout
from base.Scope import Scope


class AnonymousMessager(slixmpp.ClientXMPP):

    def __init__(self,message,file_path):
        # global scope of ahenk
        scope = Scope().getInstance()

        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()
        self.registration=scope.getRegistration()
        self.event_manager = scope.getEventManager()

        self.my_jid=str(self.configuration_manager.get('CONNECTION', 'host'))


        slixmpp.ClientXMPP.__init__(self, self.my_jid,None)

        self.message=None
        self.file=None
        self.receiver=self.configuration_manager.get('CONNECTION', 'receiverjid')+'@'+self.configuration_manager.get('CONNECTION', 'host')+'/Smack'

        if file_path is not None and file_path!='':
            self.file=open(file_path, 'rb')
        if message is not None:
            self.message=message

        self.logger.debug('[MessageSender] XMPP Receiver parameters were set')

        self.add_listeners()
        self.register_extensions()

    def add_listeners(self):
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.recv_direct_message)
        self.add_event_handler("socks5_connected", self.stream_opened)
        self.add_event_handler("socks5_data", self.stream_data)
        self.add_event_handler("socks5_closed", self.stream_closed)
        self.logger.debug('[MessageSender] Event handlers were added')


    def recv_direct_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            self.logger.debug("[MessageSender] Received message: %s -> %s" % (msg['from'], msg['body']))
            self.disconnect()
            self.logger.debug('[MessageSender] Disconnecting...')
            self.logger.debug('[MessageSender] Fired event is: confirm_registration')
            self.event_manager.fireEvent('confirm_registration',str(msg['body']))
            ##TODO type fire -- only anonymous account can fire confirm_registration

    @asyncio.coroutine
    def session_start(self, event):
        self.logger.debug('[MessageSender] Session was started')
        self.get_roster()
        self.send_presence()

        if self.message is not None:
            self.send_direct_message(self.message)

        if self.file is not None:
            self.logger.debug('[MessageSender] Sending file: '+self.file.name)
            try:
                self.logger.debug('[MessageSender] Handshaking for file transfering...')
                # Open the S5B stream in which to write to.
                proxy = yield from self['xep_0065'].handshake(self.receiver)
                # Send the entire file.
                self.logger.debug('[MessageSender] Started to streaming file...')
                while True:
                    data = self.file.read(1048576)
                    if not data:
                        break
                    yield from proxy.write(data)
                # And finally close the stream.
                proxy.transport.write_eof()
            except (IqError, IqTimeout):
                self.logger.error('[MessageSender] File transfer errored')
            else:
                self.logger.debug('[MessageSender] File transfer finished successfully')
            finally:
                self.file.close()

    def stream_opened(self, sid):
        self.logger.debug('[MessageSender] Stream was opened. Stream id: '+str(self.stream_id))
        self.file = open(self.receive_file_path+self.stream_id, 'wb')
        return self.file

    def stream_data(self, data):
        self.logger.debug('[MessageSender] Receiving file...')
        self.file.write(data)

    def stream_closed(self, exception):
        self.logger.debug('[MessageSender] Stream was closed')
        self.file.close()
        self.logger.debug('[MessageSender] Disconnecting...')
        self.disconnect()

    def send_direct_message(self,msg):
        self.logger.debug('[MessageSender] Sending message: '+msg)
        self.send_message(mto=self.receiver,mbody=msg,mtype='normal')

    def connect_to_server(self):# Connect to the XMPP server and start processing XMPP stanzas.
        try:
            self.logger.debug('[MessageSender] Connecting to server...')
            self.connect()
            self.process(forever=False)
            self.logger.debug('[MessageSender] Connection were established successfully')
            return True
        except Exception as e:
            self.logger.error('[MessageSender] Connection to server is failed! '+e)
            return False

    def register_extensions(self):
        try:
            self.register_plugin('xep_0030') # Service Discovery
            self.register_plugin('xep_0045') # Multi-User Chat
            self.register_plugin('xep_0199') # XMPP Ping
            self.register_plugin('xep_0065', {'auto_accept': True}) # SOCKS5 Bytestreams
            self.register_plugin('xep_0047', {'auto_accept': True}) # In-band Bytestreams

            self.logger.debug('[MessageSender] Extension were registered: xep_0030,xep_0045,xep_0199,xep_0065,xep_0047')
            return True
        except Exception as e:
            self.logger.error('[MessageSender] Extension registration is failed!(%s)\n' % (e.errno, e.strerror))
            return False
