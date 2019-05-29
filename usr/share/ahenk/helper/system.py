#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, signal

class ProcEntry(object):

    def __init__(self, name, pid, cmdline, euid, egid):
        super(ProcEntry, self).__init__()
        self.name = name
        self.pid = pid
        self.cmdline = cmdline
        self.euid = euid
        self.egid = egid

    def __str__(self):
        return 'name: {0}, pid: {1}, uid: {2}, gid: {3}, cmd: {4}' \
                .format(self.name, self.pid, self.euid, self.egid, self.cmdline)


class ProcParseError(Exception):

    def __init__(self, msg):
        super(Exception, self).__init__(msg)


def proclist():
    def raise_if_less(l, n):
        if len(l) < n:
            raise ProcParseError('too few fields, expected at least ' + str(n))

    for pid in [pid for pid in os.listdir('/proc') if pid.isdigit()]:
        p = os.path.join('/proc', pid, 'cmdline')
        cmdline = open(p).read()
        p = os.path.join('/proc', pid, 'status')
        euid = None
        egid = None
        name = None
        for lin in open(p):
            if lin.startswith('Name:'):
                s = lin.split()
                raise_if_less(s, 2)
                name = s[1]
            elif lin.startswith('Uid:'):
                uid_line = lin.split()
                raise_if_less(uid_line, 3)
                euid = int(uid_line[2])
            elif lin.startswith('Gid:'):
                gid_line = lin.split()
                raise_if_less(gid_line, 3)
                egid = int(gid_line[2])

        yield ProcEntry(name, int(pid), cmdline, euid, egid)

PATH_SHELLS='/etc/shells'

def login_shells():
    valid = lambda s: s.rstrip(' \n') and not s.lstrip(' \t').startswith('#')
    return [lin.rstrip('\n') for lin in open(PATH_SHELLS).readlines()
            if valid(lin)]

def shell_is_interactive(sh):
    shells = ['sh', 'bash', 'dash', 'zsh', 'fish', 'ksh', 'csh', 'tcsh']
    return any(s == os.path.basename(sh) for s in shells)

def killuserprocs(uid):
    for p in proclist():
        if p.euid == uid:
            try:
                os.kill(p.pid, signal.SIGTERM)
            except ProcessLookupError as e:
                # The process might have died immediately, up till now, even
                # before we had a chance to send a signal to it.
                pass
