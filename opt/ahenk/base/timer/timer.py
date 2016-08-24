#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import time
import threading


class Timer(threading.Thread):
    def __init__(self, timeout, timeout_function, checker_func=None, checker_success_function=None, **kwargs):
        threading.Thread.__init__(self)
        self.timeout = int(timeout)
        self.timeout_function = timeout_function
        self.timeout_function_args = None
        self.checker_func_args = None
        self.checker_success_function_args = None

        if kwargs is not None and kwargs['kwargs'] is not None:
            if 'timeout_args' in kwargs['kwargs']:
                self.timeout_function_args = kwargs['kwargs']['timeout_args']

            if 'checker_args' in kwargs['kwargs']:
                self.checker_func_args = kwargs['kwargs']['checker_args']

            if 'success_args' in kwargs['kwargs']:
                self.checker_success_function_args = kwargs['kwargs']['success_args']

        self.checker_func = checker_func
        self.checker_success_function = checker_success_function

    def run_function(self, function, parameter=None):
        if function is not None:
            if parameter is None:
                function()
            else:
                function(parameter)

    def run(self):
        timer = self.timeout

        while timer > 0:

            if self.checker_func is not None:
                if self.checker_func_args is not None:
                    if self.checker_func(self.checker_func_args) is True:
                        self.run_function(self.checker_success_function, self.checker_success_function_args)
                        return
                else:
                    if self.checker_func() is True:
                        self.run_function(self.checker_success_function, self.checker_success_function_args)
                        return

            time.sleep(1)
            timer -= 1
        if self.timeout_function_args is not None:
            self.timeout_function(self.timeout_function_args)
        else:
            self.timeout_function()
