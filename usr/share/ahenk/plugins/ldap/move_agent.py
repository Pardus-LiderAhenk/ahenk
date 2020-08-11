#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <hasankara@pardus.org.tr>


from base.model.enum.content_type import ContentType
import json

from base.plugin.abstract_plugin import AbstractPlugin


class MoveAgent(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def update_dn(self, jid, new_dn):
        cols = ['dn']
        values = [new_dn]
        return self.db_service.update('registration', cols, values, 'jid=\''+jid+'\'')

    def get_cn_from_dn(self, dn):
        if dn != None and str(dn) != "":
            dn_str_arr = str(dn).split(",")
            if len(dn_str_arr) > 0:
                return dn_str_arr[0]

    def handle_task(self):
        try:
            dn = self.data['dn']
            new_parent_dn = self.data['new_parent_dn']
            directory_server = self.data['directory_server']

            jid = self.db_service.select_one_result('registration', 'jid', 'registered = 1')
            new_dn = str(dn).replace(dn, self.get_cn_from_dn(dn) + ',' + str(new_parent_dn))
            self.update_dn(jid, new_dn)

            if directory_server == "LDAP":
                # update SSSD conf agent DN
                sssd_config_file_path = "/etc/sssd/sssd.conf"
                file_sssd = open(sssd_config_file_path, 'r')
                file_data = file_sssd.read()
                old_dn_in_sssd = ""
                new_dn_in_sssd = "ldap_default_bind_dn = " + new_dn + "\n"
                with open(sssd_config_file_path) as fp:
                    for line in fp:
                        if line.startswith('ldap_default_bind_dn'):
                            old_dn_in_sssd = line
                file_data = file_data.replace(old_dn_in_sssd, new_dn_in_sssd)

                file_sssd.close()
                file_sssd = open(sssd_config_file_path, 'w')
                file_sssd.write(file_data)
                file_sssd.close()

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ahenk başarı ile taşındı.',
                                         data=json.dumps({'Dn': new_dn}),
                                         content_type=ContentType.APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error("Error occured while moving agent. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ahenk taşınırken hata olustu' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)

def handle_task(task, context):
    cls = MoveAgent(task, context)
    cls.handle_task()

