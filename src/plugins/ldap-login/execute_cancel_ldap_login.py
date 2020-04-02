#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.plugin.abstract_plugin import AbstractPlugin
from base.registration.execute_cancel_ldap_login import ExecuteCancelLDAPLogin
from base.registration.execute_cancel_sssd_authentication import ExecuteCancelSSSDAuthentication

class CancelLDAPLogin(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.ldap_login = ExecuteCancelLDAPLogin()
        self.sssd_authentication = ExecuteCancelSSSDAuthentication()

    def handle_task(self):
        try:
            self.sssd_authentication.cancel()

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message= 'LDAP kullanıcısı ile oturum açabilme başarıyla iptal edildi.',
                                         content_type= self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='LDAP kullanıcısı ile oturum açabilme iptal edilirken hata oluştu.: {0}'.format(str(e)))

def handle_task(task, context):
    plugin = CancelLDAPLogin(task, context)
    plugin.handle_task()