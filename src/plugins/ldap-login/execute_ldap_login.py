#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.plugin.abstract_plugin import AbstractPlugin
from base.registration.execute_ldap_login import ExecuteLDAPLogin
from base.registration.execute_sssd_authentication import ExecuteSSSDAuthentication


class LDAPLogin(AbstractPlugin):

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.ldap_login = ExecuteLDAPLogin()
        self.sssd_authentication = ExecuteSSSDAuthentication()

    def handle_task(self):
        try:
            server_address = self.data['server-address']
            dn = self.data['dn']
            # version = self.data['version']
            admin_dn = self.data['admin-dn']
            admin_password = self.data['admin-password']

            # self.ldap_login.login(server_address, dn, version, admin_dn, admin_password)
            execution_result = self.sssd_authentication.authenticate(server_address, dn, admin_dn, admin_password)

            if execution_result is False:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='LDAP kullanıcısı ile oturum açma ayarlanırken hata oluştu.: SSSD Paketleri indirilemedi.',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='LDAP kullanıcısı ile oturum açma başarı ile sağlandı.',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='LDAP kullanıcısı ile oturum açma ayarlanırken hata oluştu.: {0}'.format(str(e)))

def handle_task(task, context):
    plugin = LDAPLogin(task, context)
    plugin.handle_task()
