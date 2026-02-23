#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json
import sys
import socket
from base.util.util import Util
import time
from base.system.system import System

import pwd
import os
import asyncio

from helper import system as sysx

from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError, IqTimeout
from base.scope import Scope
from base.agreement.confirm import show_message


sys.path.append('../..')


class AnonymousMessenger(ClientXMPP):
    def __init__(self, message, host= None, servicename= None):
        # global scope of ahenk
        scope = Scope().get_instance()

        self.logger = scope.get_logger()
        self.configuration_manager = scope.get_configuration_manager()
        self.registration = scope.get_registration()
        self.event_manager = scope.get_event_manager()

        if host is not None and servicename is not None:
            self.host = str(host)
            self.service = str(servicename)
        else:
            self.host = str(socket.gethostbyname(self.configuration_manager.get('CONNECTION', 'host')))
            self.service = str(self.configuration_manager.get('CONNECTION', 'servicename'))
        self.port = int(self.configuration_manager.get('CONNECTION', 'port'))

        super().__init__(self.service, None)

        self.message = message
        self.receiver_resource = self.configuration_manager.get('CONNECTION', 'receiverresource')
        self.receiver = self.configuration_manager.get('CONNECTION','receiverjid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename')
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

    async def session_start(self, event):
        self.logger.debug('Session was started')
        self.send_presence()
        try:
            await self.get_roster()
        except (IqError, IqTimeout) as e:
            self.logger.error('Roster retrieval failed. Error Message: {0}'.format(str(e)))

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
            self.logger.debug('Connecting to server... Host: {0}, Port: {1}'.format(self.host, self.port))
            
            # Configure plain auth for slixmpp
            try:
                self.register_plugin('feature_mechanisms')
                if 'feature_mechanisms' in self.plugin:
                    self['feature_mechanisms'].unencrypted_plain = True
                    self.logger.debug('Plain auth enabled')
            except Exception as plugin_error:
                self.logger.warning('Could not configure plain auth: {0}'.format(str(plugin_error)))
            
            # Standard slixmpp API usage pattern
            
            try:
                # Get or create event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Connect to server (returns Future)
                self.logger.debug('Starting connection...')
                future = self.connect(host=self.host, port=int(self.port))
                
                # Wait for connection to complete
                loop.run_until_complete(future)
                self.logger.debug('Socket connected, waiting for session_start event...')
                
                # Wait for session_start event (timeout: 30 seconds)
                try:
                    self.logger.debug('Waiting for session_start event...')
                    loop.run_until_complete(self.wait_until('session_start', timeout=30))
                    self.logger.debug('Session started successfully!')
                    
                    # For blocking mode, wait until session_end or timeout
                    # Note: disconnect() will be called from recv_direct_message when response received
                    try:
                        self.logger.debug('Waiting for session_end event (or timeout)...')
                        # Store loop reference for disconnect handling
                        self._event_loop = loop
                        loop.run_until_complete(self.wait_until('session_end', timeout=300))
                        self.logger.debug('Session ended')
                    except asyncio.TimeoutError:
                        self.logger.warning('Wait timeout reached for session_end')
                    except Exception as wait_error:
                        self.logger.error('Wait error: {0}'.format(str(wait_error)))
                    finally:
                        # Clean up event loop reference
                        if hasattr(self, '_event_loop'):
                            delattr(self, '_event_loop')
                        # Stop the event loop if still running
                        try:
                            if not loop.is_closed():
                                # Cancel all pending tasks
                                pending = asyncio.all_tasks(loop)
                                for task in pending:
                                    task.cancel()
                                # Stop the loop
                                loop.stop()
                        except Exception as cleanup_error:
                            self.logger.warning('Error during cleanup: {0}'.format(str(cleanup_error)))
                    
                    self.logger.debug('Connection established successfully')
                    return True
                except asyncio.TimeoutError:
                    self.logger.error('Connection failed - session_start timeout (XMPP stream did not start)')
                    return False
                except Exception as session_error:
                    self.logger.error('Session start error: {0}'.format(str(session_error)))
                    return False
            except Exception as e:
                self.logger.error('Connection error: {0}'.format(str(e)))
                import traceback
                self.logger.error(traceback.format_exc())
                return False
        except Exception as e:
            self.logger.error('Connection to server is failed! Error Message: {0}'.format(str(e)))
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def recv_direct_message(self, msg):
        if msg['type'] in ['normal']:

            self.logger.info('Reading registration reply')
            j = json.loads(str(msg['body']))
            message_type = j['type']
            status = str(j['status']).lower()
            dn = str(j['agentDn'])
            self.logger.debug('Registration status: ' + str(status))
            is_password = False
            body_without_password = json.loads(str(msg['body']))
            for key, value in body_without_password.items():
                if "password" in key.lower():
                    body_without_password[key] = "********"
                    is_password = True
            if is_password:
                self.logger.info('---------->Received message: {0}'.format(str(body_without_password)))
            else:
                self.logger.info('---------->Received message: {0}'.format(str(msg['body'])))

            if 'not_authorized' == str(status):
                self.logger.debug('[REGISTRATION IS FAILED]. User not authorized')
                show_message('Bilgisayar Lider MYS ye alınamadı! Sadece yetkili kullanıcılar kayıt yapabilir.', 'Kullanıcı Yetkilendirme Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()
                # Stop event loop if it exists
                if hasattr(self, '_event_loop'):
                    try:
                        loop = self._event_loop
                        if not loop.is_closed():
                            loop.call_soon_threadsafe(loop.stop)
                    except Exception as e:
                        self.logger.warning('Error stopping event loop: {0}'.format(str(e)))
            elif 'registered' == str(status) or 'registered_without_ldap' == str(status):
                try:
                    self.logger.info('Registred from server. Registration process starting.')
                    self.event_manager.fireEvent('REGISTRATION_SUCCESS', j)
                    if self.registration.showUserNotify is True:
                        show_message(f'{self.host} Etki Alanına hoş geldiniz.' \
                                    '\n\nDeğişikliklerin etkili olması için sistem yeniden başlatılacaktır. ', 'UYARI')
                    time.sleep(3)
                    self.logger.info('Disconnecting...')
                    self.disconnect()
                    # Stop event loop if it exists
                    if hasattr(self, '_event_loop'):
                        try:
                            loop = self._event_loop
                            if not loop.is_closed():
                                loop.call_soon_threadsafe(loop.stop)
                        except Exception as e:
                            self.logger.warning('Error stopping event loop: {0}'.format(str(e)))
                    self.logger.info('Rebooting...')
                    #System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
                    #sys.exit(2)
                    Util.shutdown()

                except Exception as e:
                    self.logger.error('Error Message: {0}.'.format(str(e)))
                    if self.registration.showUserNotify == True:
                        show_message(f'Bilgisayar Lider MYS ye alınamadı. Hata: {e}')
                    self.logger.debug('Disconnecting...')
                    self.disconnect()
                    # Stop event loop if it exists
                    if hasattr(self, '_event_loop'):
                        try:
                            loop = self._event_loop
                            if not loop.is_closed():
                                loop.call_soon_threadsafe(loop.stop)
                        except Exception as e:
                            self.logger.warning('Error stopping event loop: {0}'.format(str(e)))
            elif 'already_exists' == str(status):
                self.logger.debug('[REGISTRATION IS FAILED] - Hostname already in use!')
                if self.registration.showUserNotify == True:
                    show_message('{0} bilgisayar adı zaten kullanılmaktadır. Lütfen bilgisayar adını değiştirerek tekrar deneyiniz'.format(System.Os.hostname()),
                                      'Bilgisayar İsimlendirme Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()

            elif 'registration_error' == str(status):
                self.logger.info('[REGISTRATION IS FAILED] - New registration request will send')
                #self.event_manager.fireEvent('REGISTRATION_ERROR', str(j))
                if self.registration.showUserNotify == True:
                    show_message('Ahenk Lider MYS ye alınamadı. Kayıt esnasında hata oluştu. Lütfen sistem yöneticinize başvurunuz', 'Sistem Hatası')
                self.logger.debug('Disconnecting...')
                self.disconnect()
                # Stop event loop if it exists
                if hasattr(self, '_event_loop'):
                    try:
                        loop = self._event_loop
                        if not loop.is_closed():
                            loop.call_soon_threadsafe(loop.stop)
                    except Exception as e:
                        self.logger.warning('Error stopping event loop: {0}'.format(str(e)))
            else:
                self.event_manager.fireEvent(message_type, str(msg['body']))
                self.logger.debug('Fired event is: {0}'.format(message_type))

    def send_direct_message(self, msg):
        body = json.loads(str(msg))
        if body['type'] == "REGISTER" or body['type'] == "UNREGISTER":
            is_password = False
            for key, value in body.items():
                if "password" in key.lower():
                    body[key] = "********"
                    is_password = True
            if is_password:
                self.logger.info('<<--------Sending message: {0}'.format(body))
        else:
            self.logger.info('<<--------Sending message: {0}'.format(msg))
        self.send_message(mto=self.receiver, mbody=msg, mtype='normal')