#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum

class ScriptType(Enum):
    BASH = ('.sh', 'bash')
    PYTHON = ('.py', 'python')
    PERL = ('.pl', 'perl')
    RUBY = ('.rb', 'ruby')

    def get_extension(self):
        return self.value[0] 

    def get_command(self):
        return self.value[1] 
