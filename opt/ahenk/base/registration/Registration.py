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
        scope = Scope().getInstance()
        self.conf_manager = scope.getConfigurationManager()
        self.logger=scope.getLogger()

        if self.conf_manager.has_section('REGISTRATION'):
            if self.conf_manager.get('REGISTRATION', 'registered')=='false':
                self.re_register()
            else:
                self.logger.debug('[Registration] already registered')
        else:
            self.register()
            self.registration_reply=""
        self.logger.debug('[Registration] ')

    def confirm_registration(self):
        if self.registration_reply != "":
            j = json.loads(self.registration_reply)
            self.logger.info('[REGISTRATION] register reply: '+j['message'])
            status =j['status']
            dn=j['dn']

            if(str(status).lower()=='registered'):
                if self.conf_manager.has_section('CONNECTION') and self.conf_manager.get('REGISTRATION', 'from') is not None:
                    self.conf_manager.set('CONNECTION', 'uid',self.conf_manager.get('REGISTRATION', 'from'))
                    self.conf_manager.set('CONNECTION', 'password',self.conf_manager.get('REGISTRATION', 'password'))
                    self.conf_manager.set('REGISTRATION', 'dn',dn)
                    self.conf_manager.set('REGISTRATION', 'registered','true')
                    with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                        self.conf_manager.write(configfile)

                self.logger.info('[REGISTRATION] registered successfully')
                return True
            elif(status=='registration_error'):
                self.logger.info('[REGISTRATION] registration error')
                return False
            elif(status=='already_registered'):
                self.logger.info('[REGISTRATION]already registered')
                return False

    def is_registered(self):
        if self.conf_manager.has_section('REGISTRATION') and (self.conf_manager.get('REGISTRATION', 'registered')=='true'):
            return True
        else:
            return False

    def get_registration_request_message(self):
        self.logger.debug('[Registration] creating registration message according to parameters of registration')

        if self.conf_manager.has_section('REGISTRATION'):
            data = {}
            data['message_type'] = 'registration'
            data['from'] = str(self.conf_manager.get('REGISTRATION','from'))
            data['password'] = str(self.conf_manager.get('REGISTRATION','password'))
            data['mac_address'] = str(self.conf_manager.get('REGISTRATION','mac_address'))
            data['ip_address'] = str(self.conf_manager.get('REGISTRATION','ip_address'))
            data['hostname'] = str(self.conf_manager.get('REGISTRATION','hostname'))
            data['timestamp'] = str(self.conf_manager.get('REGISTRATION','timestamp'))
            data['dn'] = str(self.conf_manager.get('REGISTRATION','dn'))
            self.logger.debug('[Registration] json of registration message was created')

            json_data = json.dumps(data)
            self.logger.debug('[Registration] json converted to str')
            return json_data
        else:
            print("reg sec yok :(")
            return None

    def register(self):
        self.logger.debug('[Registration] configuration parameters of registration is checking')
        if self.conf_manager.has_section('REGISTRATION'):
            self.logger.debug('[Registration] REGISTRATION section is already created')
        else:
            self.logger.debug('[Registration] creating REGISTRATION section')

            self.conf_manager.add_section('REGISTRATION')
            self.conf_manager.set('REGISTRATION', 'from',str(self.generate_uuid(True)))
            self.conf_manager.set('REGISTRATION', 'mac_address',str(':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))))
            self.conf_manager.set('REGISTRATION', 'ip_address',str(self.get_ip_addresses()))
            self.conf_manager.set('REGISTRATION', 'hostname',str(socket.gethostname()))
            self.conf_manager.set('REGISTRATION', 'timestamp',str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M")))
            self.conf_manager.set('REGISTRATION', 'password',str(self.generate_password()))
            self.conf_manager.set('REGISTRATION', 'dn','')
            self.conf_manager.set('REGISTRATION', 'registered','false')

            #TODO self.conf_manager.configurationFilePath attribute error ? READ olacak
            self.logger.debug('[Registration] parameters were set up, section will write to configuration file')
            with open('/etc/ahenk/ahenk.conf', 'a') as configfile:
                self.conf_manager.write(configfile)
            self.logger.debug('[Registration] REGISTRATION section wrote to configuration file successfully')

    def unregister(self):
        if self.conf_manager.has_section('REGISTRATION'):
            self.conf_manager.remove_section('REGISTRATION')
            self.conf_manager.set('CONNECTION', 'uid','')
            self.conf_manager.set('CONNECTION', 'password','')
            with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                self.conf_manager.write(configfile)


    def generate_uuid(self,depend_mac=True):
        self.logger.debug('[Registration] universal user id will be created')
        if depend_mac is False:
            self.logger.debug('[Registration] uuid creating randomly')
            return uuid.uuid4() # make a random UUID
        else:
            self.logger.debug('[Registration] uuid creating depends to mac address')
            return uuid.uuid3(uuid.NAMESPACE_DNS, str(get_mac()))# make a UUID using an MD5 hash of a namespace UUID and a mac address

    def generate_password(self):
        return uuid.uuid4()

    def get_ip_addresses(self):
        self.logger.debug('[Registration] looking for network interces')
        ip_address=""
        for interface in netifaces.interfaces():
            if(str(interface) != "lo"):
                ip_address+=str(netifaces.ifaddresses(interface)[netifaces.AF_INET])
        self.logger.debug('[Registration] returning ip addresses from every interfaces')
        return ip_address
