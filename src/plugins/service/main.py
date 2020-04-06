#!/usr/bin/python3
# -*- coding: utf-8 -*-

def info():
    inf = dict()
    inf['name'] = 'service'
    inf['version'] = '1.0.0'
    inf['support'] = 'debian'
    inf['description'] = 'Agent machine all service settings (service start/stop operations, run a service/services as a start-up service...etc.) are defined with this plugin.'
    inf['task'] = True
    inf['user_oriented'] = False
    inf['machine_oriented'] = False
    inf['developer'] = 'cemre.alpsoy@agem.com.tr'

    return inf
