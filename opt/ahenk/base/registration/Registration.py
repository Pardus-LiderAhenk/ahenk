#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.logger.AhenkLogger import Logger
from base.Scope import Scope
from uuid import getnode as get_mac
import json
import uuid
import sys,logging
import datetime
import time
import netifaces
import re
import socket
import configparser


class Registration():

    #TODO try catches

    def __init__(self):
        scope = Scope.getInstance()
        self.conf_manager = scope.getConfigurationManager()
        self.logger=scope.getLogger()

        self.logger.debug('[Registration] creating registration')
        self.message=""
        self.mac = ':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
        self.uid = self.generate_uuid(True)
        self.time_stamp = datetime.datetime.now().strftime("%d-%m-%Y %I:%M")
        self.ip_address = self.get_ip_addresses()
        self.host_name =socket.gethostname()
        self.logger.debug('[Registration] registration parameters were set up')

        #print("to do create jid"+str(self.generate_uuid(True)))

    def get_registration_message(self):
        self.logger.debug('[Registration] creating registration message according to parameters of registration')
        data = {}
        data['message_type'] = 'registration'
        data['from'] = str(self.uid)
        data['password'] = 'password'
        data['mac_address'] = str(self.mac)
        data['ip_address'] = str(self.ip_address)
        data['hostname'] = str(self.host_name)
        data['timestamp'] = str(self.time_stamp)
        self.logger.debug('[Registration] json of registration message was created')

        json_data = json.dumps(data)
        self.logger.debug('[Registration] json converted to str')
        return json_data

    def register(self):
        self.logger.debug('[Registration] configuration parameters of registration is checking')
        if self.conf_manager.has_section('REGISTRATION'):
            self.logger.debug('[Registration] REGISTRATION section is already created')
        else:
            self.logger.debug('[Registration] creating REGISTRATION section')
            config = configparser.RawConfigParser()
            config.add_section('REGISTRATION')
            config.set('REGISTRATION', 'from',str(self.uid))
            config.set('REGISTRATION', 'mac_address',str(self.mac))
            config.set('REGISTRATION', 'ip_address',str(self.ip_address))
            config.set('REGISTRATION', 'hostname',str(self.host_name))
            config.set('REGISTRATION', 'timestamp',str(self.time_stamp))
            config.set('REGISTRATION', 'password',str('password'))
            config.set('REGISTRATION', 'registered','false')

            #TODO self.conf_manager.configurationFilePath attribute error ?
            self.logger.debug('[Registration] parameters were set up, section will write to configuration file')
            with open('/etc/ahenk/ahenk.conf', 'a') as configfile:
                config.write(configfile)
            self.logger.debug('[Registration] REGISTRATION section wrote to configuration file successfully')

    def generate_uuid(self,depend_mac=True):
        self.logger.debug('[Registration] universal user id will be created')
        if depend_mac is False:
            self.logger.debug('[Registration] uuid creating randomly')
            return uuid.uuid4() # make a random UUID
        else:
            self.logger.debug('[Registration] uuid creating depends to mac address')
            return uuid.uuid3(uuid.NAMESPACE_DNS, str(get_mac()))# make a UUID using an MD5 hash of a namespace UUID and a mac address

    def get_ip_addresses(self):
        self.logger.debug('[Registration] looking for network interces')
        ip_address=""
        for interface in netifaces.interfaces():
            if(str(interface) != "lo"):
                ip_address+=str(netifaces.ifaddresses(interface)[netifaces.AF_INET])
        self.logger.debug('[Registration] returning ip addresses from every interfaces')
        return ip_address
