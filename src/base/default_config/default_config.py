#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# checked config when restarted agent service. Example, sssd language settings..

from base.scope import Scope
from base.util.util import Util


class DefaultConfig:

    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()

    def check_sssd_settings(self):
        # configure sssd for language environment
        sssd_language_conf = "/etc/default/sssd"
        sssd_conf_path = "/etc/sssd/sssd.conf"
        ad_info = "/etc/ahenk/ad_info"
        registration = Scope.get_instance().get_registration()
        if registration.is_registered() and Util.is_exist(sssd_language_conf):
            file_default_sssd = open(sssd_language_conf, 'r')
            file_data = file_default_sssd.read()
            file_default_sssd.close()

            if "LC_ALL=\"tr_CY.UTF-8\"" not in file_data:
                file_data = file_data + "\n" + "LC_ALL=\"tr_CY.UTF-8\""
                self.logger.info("added language environment for sssd")
                file_default_sssd = open(sssd_language_conf, 'w')
                file_default_sssd.write(file_data)
                file_default_sssd.close()
                Util.execute("systemctl restart sssd.service")

        if registration.is_registered() and Util.is_exist(sssd_conf_path) and Util.is_exist(ad_info):
            sssd_conf_data = Util.read_file_by_line(sssd_conf_path)

            isExist = False
            for line in sssd_conf_data:
                if "ad_domain" in line:
                    isExist = True
            if isExist:
                sssd_conf_temp = open(sssd_conf_path, 'w')
                for line in sssd_conf_data:
                    if "ad_domain" in line:
                        line = line.replace("ad_domain", "ad_server")
                    sssd_conf_temp.write(line)
                sssd_conf_temp.close()
                Util.execute("systemctl restart sssd.service")
                self.logger.info("replaced ad_domain parameter with ad_server")
                sssd_conf_temp.close()


