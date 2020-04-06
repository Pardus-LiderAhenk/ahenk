#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
from base.plugin.abstract_plugin import AbstractPlugin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fstab import Fstab


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.username = str(context.get_username())
        self.mount = 'mount -o remount /home'
        self.quotacheck = 'quotacheck -cfmvF vfsv0 /home'
        self.quotaon_all = 'quotaon --all'
        self.quotaon_avug = 'quotaon -avug'
        self.set_quota = 'setquota -u {0} {1} {2} 0 0 /home'
        self.logger = self.get_logger()

    def handle_safe_mode(self):
        if self.is_exist('default_quota'):
            quota_size = self.read_file('default_quota')

            try:
                # Check fstab & append 'usrquota' option if not exists
                #fs = Fstab()
                #fs.read('/etc/fstab')
                #fstab_entries = []
                #fslines = fs.lines
                #for line in fslines:'
                #    if line.has_filesystem() and 'usrquota' not in line.options:
                #        if line.dict['directory'] == '/' or line.dict['directory'] == '/home/':
                #            self.logger.debug('Appending \'usrquota\' option to {}'.format(line.dict['directory']))
                #            line.options += ['usrquota']
                #            fstab_entries.append(line.dict['directory'])
                #fs.write('/etc/fstab')#

                # Re-mount necessary fstab entries
                #for entry in fstab_entries:
                #    self.execute(self.mount.format(entry))
                #    self.logger.debug('Remounting fstab entry {}'.format(entry))

                self.execute(self.quotacheck)
                self.logger.debug('{}'.format(self.quotacheck))

                self.execute(self.quotaon_all)
                self.logger.debug('{}'.format(self.quotaon_all))

                self.execute(self.quotaon_avug)
                self.logger.debug('{}'.format(self.quotaon_avug))

                self.execute(self.set_quota.format(self.username, quota_size, quota_size))
                self.logger.debug(
                    'Set soft and hard quota. Username: {0}, Soft Quota: {1}, Hard Quota: {2}'.format(self.username,quota_size,quota_size))


            except Exception as e:
                self.logger.error('[DiskQuota] A problem occurred while handling browser profile: {0}'.format(str(e)))


def handle_mode(context):
    safe = Safe(context)
    safe.handle_safe_mode()