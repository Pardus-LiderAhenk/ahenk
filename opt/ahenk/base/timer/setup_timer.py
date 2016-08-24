#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

class SetupTimer:
    @staticmethod
    def start(timer):
        timer.setDaemon(True)
        timer.start()
