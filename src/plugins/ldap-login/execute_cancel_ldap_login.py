#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>
# Author: Tuncay ÇOLAK<tuncay.colak@tubitak.gov.tr>

# Cancel AD or OpenLDAP authentication task

import configparser
from base.plugin.abstract_plugin import AbstractPlugin
from base.registration.execute_cancel_ldap_login import ExecuteCancelLDAPLogin
from base.registration.execute_cancel_sssd_authentication import ExecuteCancelSSSDAuthentication
from base.registration.execute_cancel_sssd_ad_authentication import ExecuteCancelSSSDAdAuthentication
from base.registration.registration import Registration

class CancelLDAPLogin(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.ldap_login = ExecuteCancelLDAPLogin()
        self.sssd_authentication = ExecuteCancelSSSDAuthentication()
        self.ad_authentication = ExecuteCancelSSSDAdAuthentication()
        self.registration = Registration()
        self.config = configparser.ConfigParser()
        self.ahenk_conf_path = "/etc/ahenk/ahenk.conf"

    def handle_task(self):
        directory_type = "LDAP"
        try:
            if self.is_exist("/etc/ahenk/ad_info"):
                directory_type = "AD"
            if directory_type == "LDAP":
                self.sssd_authentication.cancel()
            else:
                self.ad_authentication.cancel()

            self.config.read(self.ahenk_conf_path)
            if self.config.has_section('MACHINE'):
                user_disabled = self.config.get("MACHINE", "user_disabled")
                self.logger.info('User disabled value:' + str(user_disabled))
                if user_disabled != 'false':
                    self.logger.info('Enable Users')

                    self.registration.enable_local_users()
                    self.config.set('MACHINE', 'user_disabled', 'false')

                    with open(self.ahenk_conf_path, 'w') as configfile:
                        self.logger.info('Opening config file ')
                        self.config.write(configfile)
                        self.logger.info('User disabled value FALSE')
                    configfile.close()
                else:
                    self.logger.info('Local users already enabled')

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='{0} kullanıcısı ile oturum açabilme başarıyla iptal edildi.'.format(directory_type),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='{0} kullanıcısı ile oturum açabilme iptal edilirken hata oluştu.: {1}'.format(directory_type, str(e)))

def handle_task(task, context):
    plugin = CancelLDAPLogin(task, context)
    plugin.handle_task()
