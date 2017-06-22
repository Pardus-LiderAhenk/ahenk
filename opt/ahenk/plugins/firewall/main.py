#!/usr/bin/python3
# -*- coding: utf-8 -*-


def info():
    inf = dict()
    inf['name'] = 'firewall'
    inf['version'] = '1.0.0'
    inf['support'] = 'debian'
    inf['description'] = 'Firewall plugin provides to get firewall rules and changing them.'
    inf['task'] = True
    inf['user_oriented'] = False
    inf['machine_oriented'] = True
    inf['developer'] = 'mine.dogan@agem.com.tr'

    return inf