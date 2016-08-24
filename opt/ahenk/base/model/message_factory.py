#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from base.model.enum.message_type import MessageType


class MessageFactory(object):
    def createMessage(self, type, message):

        if type == MessageType.TASK_RECEIVED:
            return "Message receivden response"
        elif type == MessageType.TASK_PROCESSING:
            return "Message processing response"
        else:
            return None

    createMessage = staticmethod(createMessage)
