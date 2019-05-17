#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.scope import Scope
from base.util.util import Util
import re


class ExecuteCancelLDAPLogin:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

    def cancel(self):
        self.logger.info('Purge ldap packages')
        self.util.execute("apt-get install sudo -y")
        self.util.execute("apt purge libpam-ldap libnss-ldap ldap-utils sudo-ldap nss-updatedb libnss-db libpam-ccreds -y")
        self.util.execute("apt autoremove -y")

        self.logger.info('purging successfull')

        # pattern for clearing file data from spaces, tabs and newlines
        pattern = re.compile(r'\s+')

        ldap_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/ldap"
        ldap_original_file_path = "/usr/share/pam-configs/ldap"

        pam_script_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/pam_script"
        pam_script_original_file_path = "/usr/share/pam-configs/pam_script"

        if self.util.is_exist(ldap_back_up_file_path):
            self.logger.info("Replacing {0} with {1}".format(ldap_original_file_path, ldap_back_up_file_path))
            self.util.copy_file(ldap_back_up_file_path, ldap_original_file_path)
            self.logger.info("Deleting {0}".format(ldap_back_up_file_path))
            self.util.delete_file(ldap_back_up_file_path)

        if self.util.is_exist(pam_script_back_up_file_path):
            self.logger.info(
                "Replacing {0} with {1}".format(pam_script_original_file_path, pam_script_back_up_file_path))
            self.util.copy_file(pam_script_back_up_file_path, pam_script_original_file_path)
            self.logger.info("Deleting {0}".format(pam_script_back_up_file_path))
            self.util.delete_file(pam_script_back_up_file_path)

        (result_code, p_out, p_err) = self.util.execute("DEBIAN_FRONTEND=noninteractive pam-auth-update --package")
        if result_code == 0:
            self.logger.info("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' has run successfully")
        else:
            self.logger.error(
                "'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' could not run successfully: " + p_err)

        # Configure nsswitch.conf
        file_ns_switch = open("/etc/nsswitch.conf", 'r')
        file_data = file_ns_switch.read()

        # cleared file data from spaces, tabs and newlines
        text = pattern.sub('', file_data)

        did_configuration_change = False
        if "passwd:compatldap[NOTFOUND=return]db" in text:
            file_data = file_data.replace("passwd:         compat ldap [NOTFOUND=return] db", "passwd:         compat")
            did_configuration_change = True

        if "group:compatldap[NOTFOUND=return]db" in text:
            file_data = file_data.replace("group:          compat ldap [NOTFOUND=return] db", "group:          compat")
            did_configuration_change = True

        if "shadow:compatldap" in text:
            file_data = file_data.replace("shadow:         compat ldap", "shadow:         compat")
            did_configuration_change = True

        if "#gshadow:files" in text:
            file_data = file_data.replace("#gshadow:        files", "gshadow:        files")
            did_configuration_change = True

        if did_configuration_change:
            self.logger.info("nsswitch.conf configuration has been configured")
        else:
            self.logger.info("nsswitch.conf has already been configured")

        file_ns_switch.close()
        file_ns_switch = open("/etc/nsswitch.conf", 'w')
        file_ns_switch.write(file_data)
        file_ns_switch.close()

        # Configure ldap-cache
        nss_update_cron_job_file_path = "/etc/cron.daily/nss-updatedb"
        if self.util.is_exist(nss_update_cron_job_file_path):
            self.util.delete_file(nss_update_cron_job_file_path)
            self.logger.info("{0} is deleted.".format(nss_update_cron_job_file_path))

        # Configure lightdm.service
        pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
        if self.util.is_exist(pardus_xfce_path):
            self.logger.info("99-pardus-xfce.conf exists. Deleting file.")
            self.util.delete_file(pardus_xfce_path)

        self.util.execute("systemctl restart nscd.service")
        self.logger.info("Operation finished")

