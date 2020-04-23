#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

import configparser
from base.plugin.abstract_plugin import AbstractPlugin
from base.registration.execute_ldap_login import ExecuteLDAPLogin
from base.registration.execute_sssd_authentication import ExecuteSSSDAuthentication
from base.registration.registration import Registration

class LDAPLogin(AbstractPlugin):

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.ldap_login = ExecuteLDAPLogin()
        self.sssd_authentication = ExecuteSSSDAuthentication()
        self.config = configparser.ConfigParser()
        self.registration = Registration()
        self.ahenk_conf_path = "/etc/ahenk/ahenk.conf"

    def handle_task(self):
        try:
            server_address = self.data['server-address']
            dn = self.data['dn']
            # version = self.data['version']
            admin_dn = self.data['admin-dn']
            admin_password = self.data['admin-password']

            if admin_password is None:
                self.config.read(self.ahenk_conf_path)
                if self.config.has_section('CONNECTION'):
                    admin_password = self.config.get("CONNECTION", "password")

            execution_result = self.sssd_authentication.authenticate(server_address, dn, admin_dn, admin_password)
            if execution_result is False:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='LDAP kullanıcısı ile oturum açma ayarlanırken hata oluştu.: SSSD Paketleri indirilemedi.',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                # if get disabled_local_user TRUE set user_disabled in ahenk.conf. disabled local users then client reboot
                if self.has_attr_json(self.data, 'disableLocalUser') is True:
                    disabled_local_user = self.data['disableLocalUser']
                    self.config.read(self.ahenk_conf_path)
                    if disabled_local_user is True:
                        # self.registration.disable_local_users()
                        config = configparser.ConfigParser()
                        config.read(self.ahenk_conf_path)
                        config.set('MACHINE', 'user_disabled', 'true')

                        with open(self.ahenk_conf_path, 'w') as configfile:
                            self.logger.info('Opening config file ')
                            config.write(configfile)
                        configfile.close()

                        self.logger.info('User disabled value Disabled')
                    else:
                        self.logger.info("local users will not be disabled because local_user parameter is FALSE")
                self.shutdown()

                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='LDAP kullanıcısı ile oturum açma başarı ile sağlandı ve istemci yeniden başlatılıyor.',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='LDAP kullanıcısı ile oturum açma ayarlanırken hata oluştu.: {0}'.format(str(e)))

def handle_task(task, context):
    plugin = LDAPLogin(task, context)
    plugin.handle_task()
