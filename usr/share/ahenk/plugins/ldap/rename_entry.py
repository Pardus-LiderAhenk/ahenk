#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Edip YILDIZ
# Author: Hasan Kara <hasan.kara@pardus.org.tr>


from base.model.enum.content_type import ContentType
import json, threading
from base.plugin.abstract_plugin import AbstractPlugin
from base.scope import Scope


class RenameEntry(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        scope = Scope().get_instance()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.conf_manager = scope.get_configuration_manager()
        self.hostname_file = '/etc/hostname'

    def update_dn(self, old_cn, new_cn, new_dn):
        return self.db_service.update('registration', ['jid', 'dn'], [new_cn, new_dn], ' jid = ' + '\'' + old_cn + '\'')


    def handle_task(self):
        try:
            old_dn = self.data['dn']
            old_cn = self.data['old_cn']
            new_cn = self.data['new_cn']
            directory_server = self.data['directory_server']
            new_dn = str(old_dn).replace(old_cn, new_cn)
            
            self.logger.debug('Renaming hostname from: ' + old_cn + " to: " + new_cn)
            self.write_file(self.hostname_file, new_cn)

            ## update agent db 
            jid = self.db_service.select_one_result('registration','jid','registered = 1')
            new_dn = str(old_dn).replace(old_cn, new_cn)

            self.update_dn(old_cn, new_cn, new_dn)
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

            # update ahenk.conf
            self.conf_manager.set('CONNECTION', 'uid', new_cn)
            with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                self.conf_manager.write(configfile)
            
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Ahenk adı başarı ile değiştirildi.',
                                         data=json.dumps({'Dn': new_dn}),
                                         content_type=ContentType.APPLICATION_JSON.value)
            self.execute("systemctl restart ahenk.service")


        except Exception as e:
            self.logger.error(" error on handle xmessage task. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ahenk adı değiştirilirken hata olustu' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)


def handle_task(task, context):
    cls = RenameEntry(task, context)
    cls.handle_task()
