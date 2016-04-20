#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import asyncio
import time

import slixmpp

from base.Scope import Scope


class FileTransfer(slixmpp.ClientXMPP):
    def __init__(self, file_path):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        scope = Scope().getInstance()

        self.logger = scope.getLogger()
        self.configuration_manager = scope.getConfigurationManager()

        self.file = open(file_path, 'rb')
        self.my_jid = str(self.configuration_manager.get('CONNECTION', 'uid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename') + '/sender')
        self.my_pass = str(self.configuration_manager.get('CONNECTION', 'password'))
        self.receiver = self.configuration_manager.get('CONNECTION', 'receiverjid') + '@' + self.configuration_manager.get('CONNECTION', 'servicename') + '/Smack'

        try:
            slixmpp.ClientXMPP.__init__(self, self.my_jid, self.my_pass)
        except Exception as e:
            print(str(e))

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0065')

        self.add_event_handler("session_start", self.start)

    @asyncio.coroutine
    def start(self, event):
        print('sending...')

        try:
            # Open the S5B stream in which to write to.
            proxy = yield from self['xep_0065'].handshake(self.receiver)

            # Send the entire file.
            i = 0
            while True:
                data = self.file.read(1000)
                i += 1
                print('-->'+str(i)+'--'+str(len(data)))
                if not data:
                    break
                yield from proxy.write(data)

            time.sleep(10)
            # And finally close the stream.
            proxy.transport.write_eof()

        except Exception as e:
            print('File transfer errored:' + str(e))
        else:
            print('File transfer finished')
        finally:
            self.disconnect()
            self.file.close()

    @staticmethod
    def run(file_path):
        xmpp = FileTransfer(file_path)
        xmpp.connect()
        xmpp.process(forever=False)
