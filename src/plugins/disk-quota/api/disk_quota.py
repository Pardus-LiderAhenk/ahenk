#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json
import os
import sys

from base.plugin.abstract_plugin import AbstractPlugin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fstab import Fstab


class DiskQuota(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.username = self.context.get('username')

        self.mount = 'mount -o remount /home'
        self.quotacheck = 'quotacheck -cfmvF vfsv0 /home'
        self.quotaon_all = 'quotaon --all'
        self.quotaon_avug = 'quotaon -avug'
        self.set_quota = 'setquota -u {0} {1} {2} 0 0 /home'
        self.get_quota = 'quota -u {0} | awk \'{{print $4}}\' | tail -1'

        self.parameters = json.loads(self.data)

        self.soft_quota = str(int(self.parameters['soft-quota']) * 1024)
        self.hard_quota = str(int(self.parameters['hard-quota']) * 1024)
        self.default_quota = str(int(self.parameters['default-quota']) * 1024)

        self.old_quota = None

        self.logger.debug('Parameters were initialized.')

    def handle_policy(self):
        self.logger.debug('Policy handling...')
        try:

            if 'username' in self.context.data and self.context.get('username') is not None:
                self.logger.debug('This is user profile, parameters reinitializing.')
                self.username = self.context.get('username')

            self.old_quota = self.execute(self.get_quota.format(self.username))[1]
            # Check fstab & append 'usrquota' option if not exists
            # fs = Fstab()
            # fs.read('/etc/fstab')
            # fstab_entries = []
            # fslines = fs.lines
            # for line in fslines:
            #    if line.has_filesystem() and 'usrquota' not in line.options:
            #        if line.dict['directory'] == '/' or line.dict['directory'] == '/home/':
            #            self.logger.debug('Appending \'usrquota\' option to {}'.format(line.dict['directory']))
            #            line.options += ['usrquota']
            #            fstab_entries.append(line.dict['directory'])
            # fs.write('/etc/fstab')

            # Re-mount necessary fstab entries
            # for entry in fstab_entries:
            #    self.execute(self.mount.format(entry))
            #    self.logger.debug('Remounting fstab entry {}'.format(entry))
            self.execute(self.quotacheck)
            self.logger.debug('{}'.format(self.quotacheck))

            self.execute(self.quotaon_all)
            self.logger.debug('{}'.format(self.quotaon_all))

            self.execute(self.quotaon_avug)
            self.logger.debug('{}'.format(self.quotaon_avug))

            self.execute(self.set_quota.format(self.username, self.soft_quota, self.hard_quota))
            self.logger.debug(
                'Set soft and hard quota. Username: {0}, Soft Quota: {1}, Hard Quota: {2}'.format(self.username,
                                                                                                  self.soft_quota,
                                                                                                  self.hard_quota))

            self.create_default_quota_file()

            result = dict()
            if self.context.is_mail_send():
                mail_content = self.context.get_mail_content()
                if mail_content.__contains__('{ahenk-ip}'):
                    mail_content = str(mail_content).replace('{ahenk-ip}', ' {0} IP\'li Ahenk\'teki yeni'.format(
                        str(self.Hardware.ip_addresses())))
                if mail_content.__contains__('{old-quota}'):
                    mail_content = str(mail_content).replace('{old-quota}',
                                                             ' Eski kota değeri {0} MB olan'.format(
                                                                 str(int(self.old_quota) / 1024)))
                if mail_content.__contains__('{soft-quota}'):
                    mail_content = str(mail_content).replace('{soft-quota}', str(int(self.soft_quota) / 1024) + ' MB')
                if mail_content.__contains__('{hard-quota}'):
                    mail_content = str(mail_content).replace('{hard-quota}', str(int(self.hard_quota) / 1024) + ' MB')
                if mail_content.__contains__('{default-quota}'):
                    mail_content = str(mail_content).replace('{default-quota}',
                                                             str(int(self.default_quota)/1024) + ' MB')

                self.context.set_mail_content(mail_content)
                result['mail_content'] = str(self.context.get_mail_content())
                result['mail_subject'] = str(self.context.get_mail_subject())
                result['mail_send'] = self.context.is_mail_send()

            self.context.create_response(code=self.get_message_code().POLICY_PROCESSED.value,
                                         data=json.dumps(result),
                                         message='Kotalar başarıyla güncellendi.',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('[DiskQuota] A problem occurred while handling browser profile: {0}'.format(str(e)))
            self.context.create_response(code=self.get_message_code().POLICY_ERROR.value,
                                         message='Disk Quota profili uygulanırken bir hata oluştu.')

    def create_default_quota_file(self):
        self.write_file('default_quota', self.default_quota)
