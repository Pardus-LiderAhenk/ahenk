#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class FirewallRules(AbstractPlugin):
    def __init__(self, task, context):
        super(FirewallRules, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.temp_file_name = str(self.generate_uuid())
        self.export_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)

        self.logger.debug('[FIREWALL] Parameters were initialized.')

    def handle_task(self):
        try:
            self.create_file(self.export_path)
            self.logger.debug('[FIREWALL] Export rules to a temporary file...')
            self.execute('/sbin/iptables-save > {}'.format(self.export_path))

            self.logger.debug('[FIREWALL] Reading the file...')
            with open(self.export_path, "r") as rules_file:
                firewall_rules = rules_file.readlines()

            self.logger.info('[FIREWALL] Firewall task is handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Güvenlik Duvarı kuralları başarıyla okundu.',
                                         data=json.dumps({'firewallRules': firewall_rules}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('[FIREWALL] A problem occured while handling Firewall task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Güvenlik Duvarı görevi çalıştırılırken bir hata oluştu.')


def handle_task(task, context):
    get_rules = FirewallRules(task, context)
    get_rules.handle_task()
