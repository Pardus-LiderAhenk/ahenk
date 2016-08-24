#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>


class EventBase:
    """
        This is base event class for event management.
    """

    listeners = []

    def __init__(self):
        self.listeners.append(self)
        self.listener_events = []

    def register_event(self, event_name, callback_func):
        """
            Registers event listener.
            Args:
                event_name : name of event, user specify event name
                callback_func : when an event fire with specified event name this method will call
        """
        self.listener_events.append({'event_name': event_name, 'callback_func': callback_func})


class Event:
    """
        This is event class. Takes two argument ;
        Args:
            event_name : name of event.
            callback_args : arguments specified by user. This function will transmit args to callback function directly.
    """

    def __init__(self, event_name, *callback_args):
        for listener in EventBase.listeners:
            for listener_cls in listener.listener_events:
                if listener_cls['event_name'] == event_name:
                    listener_cls['callback_func'](*callback_args)
