#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import sys
import easygui


def confirm(message, title):
    choice = easygui.buttonbox(msg=message, title=title, choices=["Tamam"])

    if choice:
        print('Y')
    else:
        print('N')


if __name__ == '__main__':

    if len(sys.argv) == 3:
        try:
            confirm(sys.argv[1], sys.argv[2])
        except Exception as e:
            print(str(e))
    else:
        print('Argument fault. Check your parameters or content of parameters. Parameters: ' + str(sys.argv))
