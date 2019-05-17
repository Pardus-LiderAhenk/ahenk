#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>


class SafeMode(object):
    def __init__(self, username):
        self.username = username

    @property
    def obj_name(self):
        return "SAFE_MODE"
