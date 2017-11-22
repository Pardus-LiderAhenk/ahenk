#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.event.event_base import EventBase, Event


class EventManager(EventBase):
    """docstring for EventManager"""

    def __init__(self):
        EventBase.__init__(self)

    def fireEvent(self, event_name, *args):
        Event(event_name, *args)
