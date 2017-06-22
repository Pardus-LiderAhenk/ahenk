#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json
import os
from base.plugin.abstract_plugin import AbstractPlugin


class FirewallRules(AbstractPlugin):
    def __init__(self, profile_data, context):
        super(FirewallRules, self).__init__()
        self.profile_data = profile_data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.parameters = json.loads(self.profile_data)
        self.plugin_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.rules = self.parameters['rules']
        self.temp_file_name = str(self.generate_uuid())
        self.file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)
        self.initial_rules_file_path = self.plugin_path + '/iptables.rules'
        self.logger.debug('[FIREWALL] Parameters were initialized.')

    def handle_policy(self):
        try:
            if not self.is_exist(self.initial_rules_file_path):
                self.logger.debug('[FIREWALL] Export initial rules to a temporary file...')
                self.execute('/sbin/iptables-save > {}'.format(self.initial_rules_file_path))

            self.logger.debug('[FIREWALL] Writing rules to temporary file...')
            self.write_file(self.file_path, '{0}{1}'.format(self.rules, '\n'))

            self.logger.debug('[FIREWALL] Adding temp file to iptables-restore as parameter...')
            result_code, p_out, p_err = self.execute('/sbin/iptables-restore < {}'.format(self.file_path))

            if p_err != '':
                raise Exception(p_err)

            self.logger.debug('[FIREWALL] Save the rules...')
            self.execute('service netfilter-persistent save')

            self.logger.debug('[FIREWALL] Restart the service...')
            self.execute('service netfilter-persistent restart')

            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value,
                                         message='Güvenlik Duvarı kuralları başarıyla kaydedildi.')
            self.logger.info('[FIREWALL] Firewall policy is handled successfully')

        except Exception as e:
            self.logger.error(
                '[FIREWALL] A problem occured while handling Firewall policy: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value,
                                         message='Güvenlik Duvarı profili uygulanırken bir hata oluştu: ' + str(e))


def handle_policy(profile_data, context):
    set_rules = FirewallRules(profile_data, context)
    set_rules.handle_policy()
