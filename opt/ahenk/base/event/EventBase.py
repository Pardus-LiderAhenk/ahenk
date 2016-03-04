#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

class EventBase():
    listeners = []
    def __init__(self):
        self.listeners.append(self)
        self.listener_events = []
    def register_event(self, event_name, callback_func):
        self.listener_events.append({'event_name' : event_name, 'callback_func' : callback_func})


class Event():
    def __init__(self, event_name, *callback_args):
        for listener in EventBase.listeners:
            for listener_cls in listener.listener_events:
                if listener_cls['event_name'] == event_name:
                    listener_cls['callback_func'](*callback_args)
