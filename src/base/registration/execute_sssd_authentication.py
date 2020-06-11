#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.scope import Scope
from base.util.util import Util
import re


class ExecuteSSSDAuthentication:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

    def authenticate(self, server_address, dn, admin_dn, admin_password):
        try:
            ldap_pwdlockout_dn = "ou=PasswordPolicies" + "," + dn

            # pattern for clearing file data from spaces, tabs and newlines
            pattern = re.compile(r'\s+')

            sssd_config_template_path = "/usr/share/ahenk/base/registration/config-files/sssd.conf"
            sssd_config_folder_path = "/etc/sssd"
            sssd_config_file_path = "/etc/sssd/sssd.conf"
            sssd_language_conf = "/etc/default/sssd"

            common_session_conf_path = "/etc/pam.d/common-session"

            # copy configuration file to /etc/sssd/sssd.conf before package installation
            # create sssd folder in /etc
            if not self.util.is_exist(sssd_config_folder_path):
                self.util.create_directory(sssd_config_folder_path)
                self.logger.info("{0} folder is created".format(sssd_config_folder_path))

            # Copy sssd.conf template under /etc/sssd
            self.util.copy_file(sssd_config_template_path, sssd_config_folder_path)
            self.logger.info("{0} config file is copied under {1}".format(sssd_config_template_path, sssd_config_folder_path))

            # Configure sssd.conf
            file_sssd = open (sssd_config_file_path, 'r')
            file_data = file_sssd.read()

            file_data = file_data.replace("###ldap_pwdlockout_dn###", "ldap_pwdlockout_dn = " + ldap_pwdlockout_dn)
            file_data = file_data.replace("###ldap_uri###", "ldap_uri = " + "ldap://" + server_address + "/")
            file_data = file_data.replace("###ldap_default_bind_dn###", "ldap_default_bind_dn = " + admin_dn)
            file_data = file_data.replace("###ldap_default_authtok###", "ldap_default_authtok = " + admin_password)
            file_data = file_data.replace("###ldap_search_base###", "ldap_search_base = " + dn)
            file_data = file_data.replace("###ldap_user_search_base###", "ldap_user_search_base = " + dn)
            file_data = file_data.replace("###ldap_group_search_base###", "ldap_group_search_base = " + dn)
            file_data = file_data.replace("###ldap_sudo_search_base###", "ldap_sudo_search_base = ou=Role,ou=Groups" + dn)

            file_sssd.close()
            file_sssd = open(sssd_config_file_path, 'w')
            file_sssd.write(file_data)
            file_sssd.close()

            # Install libpam-sss sssd-common for sssd authentication
            (result_code, p_out, p_err) = self.util.execute("sudo apt install libpam-sss sssd-common -y")

            if result_code != 0:
                self.logger.error("SSSD packages couldn't be downloaded.")
                return False

            # configure common-session for creating home directories for ldap users
            file_common_session = open(common_session_conf_path, 'r')
            file_data = file_common_session.read()

            if "session optional pam_mkhomedir.so skel=/etc/skel umask=077" not in file_data :
                file_data = file_data + "\n" + "session optional pam_mkhomedir.so skel=/etc/skel umask=077"
                self.logger.info("common-session is configured")

            file_common_session.close()
            file_common_session = open(common_session_conf_path, 'w')
            file_common_session.write(file_data)
            file_common_session.close()

            # configure sssd for language environment
            file_default_sssd = open(sssd_language_conf, 'r')
            file_data = file_default_sssd.read()

            if "LC_ALL=\"tr_CY.UTF-8\"" not in file_data :
                file_data = file_data + "\n" + "LC_ALL=\"tr_CY.UTF-8\""
                self.logger.info("/etc/default/sssd is configured")

            file_default_sssd.close()
            file_default_sssd = open(sssd_language_conf, 'w')
            file_default_sssd.write(file_data)
            file_default_sssd.close()

            self.logger.info("Restarting sssd service.")
            self.util.execute("systemctl restart sssd.service")

            # Configure nsswitch.conf
            file_ns_switch = open("/etc/nsswitch.conf", 'r')
            file_data = file_ns_switch.read()

            # cleared file data from spaces, tabs and newlines
            text = pattern.sub('', file_data)

            is_configuration_done_before = False
            if "passwd:compatsss" not in text and "passwd:compat" in text:
                file_data = file_data.replace("passwd:         compat", "passwd:         compat sss")
                is_configuration_done_before = True

            if "passwd:filessystemdsss" not in text and "passwd:filessystemd" in text:
                file_data = file_data.replace("passwd:         files systemd", "passwd:         files systemd sss")
                is_configuration_done_before = True

            if "group:compatsss" not in text and "group:compat" in text:
                file_data = file_data.replace("group:          compat", "group:          compat sss")
                is_configuration_done_before = True

            if "group:filessystemdsss" not in text and "group:filessystemd" in text:
                file_data = file_data.replace("group:          files systemd", "group:          files systemd sss")
                is_configuration_done_before = True

            if "shadow:compatsss" not in text and "shadow:compat" in text:
                file_data = file_data.replace("shadow:         compat", "shadow:         compat sss")
                is_configuration_done_before = True

            if "shadow:filessss" not in text and "shadow:files" in text:
                file_data = file_data.replace("shadow:         files", "shadow:         files sss")
                is_configuration_done_before = True

            if "services:dbfilessss" not in text:
                file_data = file_data.replace("services:       db files", "services:       db files sss")
                is_configuration_done_before = True

            if "netgroup:nissss" not in text:
                file_data = file_data.replace("netgroup:       nis", "netgroup:       nis sss")
                is_configuration_done_before = True

            if "sudoers:filessss" not in text and "sudoers:files" in text:
                file_data = file_data.replace("sudoers:        files", "sudoers:        files sss")
                is_configuration_done_before = True
            elif "sudoers:filessss" in text:
                is_configuration_done_before = False
            else:
                file_data = file_data + "sudoers:        files sss"


            if is_configuration_done_before:
                self.logger.info("nsswitch.conf configuration has been completed")
            else:
                self.logger.info("nsswitch.conf is already configured")

            file_ns_switch.close()
            file_ns_switch = open("/etc/nsswitch.conf", 'w')
            file_ns_switch.write(file_data)
            file_ns_switch.close()

            self.util.execute("systemctl restart nscd.service")
            # self.util.execute("pam-auth-update --force")
            self.logger.info("LDAP Login operation has been completed.")

            self.logger.info("LDAP Login işlemi başarı ile sağlandı.")
            return True
        except Exception as e:
            self.logger.error(str(e))
            self.logger.info("LDAP Login işlemi esnasında hata oluştu.")
            return False

