#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK<tuncay.colak@tubitak.gov.tr>

# Active Directory authentication task

import configparser
from base.plugin.abstract_plugin import AbstractPlugin
from base.registration.execute_sssd_ad_authentication import ExecuteSSSDAdAuthentication
from base.registration.registration import Registration

class ADLogin(AbstractPlugin):

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.ad_authentication = ExecuteSSSDAdAuthentication()
        self.registration = Registration()
        self.config = configparser.ConfigParser()
        self.ahenk_conf_path = "/etc/ahenk/ahenk.conf"

    def handle_task(self):
        try:
            domain_name = self.data['domain_name']
            hostname = self.data['hostname']
            ip_address = self.data['ip_address']
            ad_username = self.data['ad_username']
            admin_password = self.data['admin_password']
            ad_port = self.data['ad_port']
            disabled_local_user = self.data['disableLocalUser']

            execution_result = self.ad_authentication.authenticate(domain_name, hostname, ip_address, admin_password, ad_username)
            if execution_result is False:
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Active Directory kullanıcısı ile oturum açma ayarlanırken hata oluştu.: Gerekli Paketleri indirilemedi.',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                # if get disabled_local_user TRUE set user_disabled in ahenk.conf. disabled local users then client reboot
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
                                             message='Active Directory kullanıcısı ile oturum açma başarı ile sağlandı ve istemci yeniden başlatılıyor.',
                                             content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Active Directory kullanıcısı ile oturum açma ayarlanırken hata oluştu.: {0}'.format(str(e)))

def handle_task(task, context):
    plugin = ADLogin(task, context)
    plugin.handle_task()
