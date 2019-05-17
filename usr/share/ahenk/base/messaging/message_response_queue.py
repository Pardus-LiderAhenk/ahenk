#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import threading

from base.scope import Scope


class MessageResponseQueue(threading.Thread):
    """
        This class handles responses and sends it to lider server.
    """

    def __init__(self, outQueue):
        super(MessageResponseQueue, self).__init__()
        scope = Scope.get_instance()
        self.logger = scope.get_logger()
        self.messageManager = scope.get_messenger()
        self.outQueue = outQueue

    def run(self):
            while True:
                try:
                    # This item will send response to lider.
                    # item must be response message. Response message may be generic message type
                    responseMessage = self.outQueue.get(block=True)
                    self.logger.debug('Sending response message to lider. Response Message ' + str(responseMessage))
                    # Call message manager for response
                    self.messageManager.send_direct_message(responseMessage)
                    # self.outQueue.task_done()
                except Exception as e:
                    self.logger.error
