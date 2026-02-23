#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import json
import sys
import socket
import asyncio
import threading
import time

from slixmpp import ClientXMPP

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

        super().__init__(self.my_jid, self.my_pass)

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

        self.port = self.configuration_manager.get('CONNECTION', 'port')
        self.logger.debug('XMPP Messager parameters were set')

        self.register_extensions()
        self.add_listeners()
        self.roster.auto_subscribe = True
        
        # Event loop management for slixmpp
        self._event_loop = None
        self._event_loop_thread = None
        self._connected = False

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

    def _run_event_loop(self, loop):
        """Run event loop in a separate thread"""
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        except Exception as e:
            self.logger.error('Event loop error: {0}'.format(str(e)))
        finally:
            loop.close()

    def connect_to_server(self):  # Connect to the XMPP server and start processing XMPP stanzas.
        try:
            # Configure plain auth for slixmpp
            try:
                self.register_plugin('feature_mechanisms')
                if 'feature_mechanisms' in self.plugin:
                    self['feature_mechanisms'].unencrypted_plain = True
                    self.logger.debug('Plain auth enabled')
            except Exception as plugin_error:
                self.logger.warning('Could not configure plain auth: {0}'.format(str(plugin_error)))
            
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            self._event_loop = loop
            
            # Start event loop in a separate thread
            self._event_loop_thread = threading.Thread(target=self._run_event_loop, args=(loop,), daemon=True)
            self._event_loop_thread.start()
            self.logger.debug('Event loop thread started')
            
            # Wait a bit for the event loop to start
            time.sleep(0.1)
            
            # Connect to server (slixmpp uses async connect)
            self.logger.debug('Starting connection... Host: {0}, Port: {1}'.format(self.hostname, self.port))
            
            # Schedule connection in the event loop
            async def connect_async():
                try:
                    await self.connect(host=self.hostname, port=int(self.port))
                    self.logger.debug('Socket connected, waiting for session_start event...')
                    
                    # Wait for session_start event (timeout: 30 seconds)
                    try:
                        await self.wait_until('session_start', timeout=30)
                        self.logger.debug('Connection were established successfully')
                        self._connected = True
                        return True
                    except asyncio.TimeoutError:
                        self.logger.error('Connection failed - session_start timeout')
                        self._connected = False
                        return False
                    except Exception as session_error:
                        self.logger.error('Session start error: {0}'.format(str(session_error)))
                        self._connected = False
                        return False
                except Exception as e:
                    self.logger.error('Connection error: {0}'.format(str(e)))
                    self._connected = False
                    return False
            
            # Run connection in the event loop
            future = asyncio.run_coroutine_threadsafe(connect_async(), loop)
            
            # Wait for connection to complete (with timeout)
            try:
                result = future.result(timeout=35)
                if result:
                    self.logger.info('XMPP connection established successfully')
                    return True
                else:
                    self.logger.error('XMPP connection failed')
                    return False
            except Exception as e:
                self.logger.error('Connection future error: {0}'.format(str(e)))
                return False
                
        except Exception as e:
            self.logger.error('Connection to server is failed! Error Message: {0}'.format(str(e)))
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def session_end(self, event=None):
        self.logger.warning('DISCONNECTED')
        self._connected = False

    async def session_start(self, event):
        self.logger.debug('Session was started')
        self.send_presence()
        try:
            await self.get_roster()
        except Exception as e:
            self.logger.error('Roster retrieval failed. Error Message: {0}'.format(str(e)))

    def send_direct_message(self, msg):
        """Send message asynchronously through the event loop"""
        try:
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
            
            # Check if event loop is available and connected
            if self._event_loop is None or self._event_loop.is_closed():
                self.logger.error('Event loop is not available for sending message')
                return
            
            if not self._connected:
                self.logger.warning('Not connected to XMPP server, message may not be sent')
            
            # Send message in the event loop thread to ensure it's processed immediately
            def send_in_loop():
                try:
                    self.send_message(mto=self.receiver, mbody=msg, mtype='normal')
                    self.logger.debug('Message sent successfully to {0}'.format(self.receiver))
                except Exception as send_error:
                    self.logger.error('Error sending message in event loop: {0}'.format(str(send_error)))
            
            # Schedule the send operation in the event loop
            self._event_loop.call_soon_threadsafe(send_in_loop)
            
        except json.JSONDecodeError as json_error:
            self.logger.error('Invalid JSON in message: {0}'.format(str(json_error)))
        except Exception as e:
            self.logger.error(
                'A problem occurred while sending direct message. Error Message: {0}'.format(str(e)))
            import traceback
            self.logger.error(traceback.format_exc())

    def recv_direct_message(self, msg):
        if msg['type'] in ['normal']:
            try:
                j = json.loads(str(msg['body']))
                message_type = j['type']
                self.logger.debug("Get message type: "+str(message_type))

                if j['type'] == "EXECUTE_POLICY":
                    self.logger.info('---------->Received message: {0}'.format(str(msg['body'])))

                if j['type'] == "EXECUTE_TASK":
                    message = json.loads(str(msg['body']))
                    task = json.loads(str(message['task']))
                    #plugin_name = task['plugin']['name']
                    parameter_map = task['parameterMap']
                    use_file_transfer = message['fileServerConf']
                    is_password = False
                    for key, value in parameter_map.items():
                        if "password" in key.lower():
                            parameter_map[key] = "********"
                            task['parameterMap'] = parameter_map
                            message['task'] = task
                            is_password = True
                    if use_file_transfer != None:
                        #message['fileServerConf'] = "*******"
                        file_server_conf = message['fileServerConf']
                        file_server_param = file_server_conf['parameterMap']
                        for key, value in file_server_param.items():
                            if "password" in key.lower():
                                file_server_param[key] = "********"
                                file_server_conf['parameterMap'] = file_server_param
                                #message['fileServerConf']['parameterMap'] = file_server_param
                                message['fileServerConf'] = file_server_conf
                        is_password = True
                    if is_password:
                        self.logger.info('---------->Received message: {0}'.format(str(message)))
                    else:
                        self.logger.info('---------->Received message: {0}'.format(str(msg['body'])))
                self.event_manger.fireEvent(message_type, str(msg['body']))
                self.logger.debug('Fired event is: {0}'.format(message_type))
            except Exception as e:
                self.logger.error(
                    'A problem occurred while keeping message. Error Message: {0}'.format(str(e)))