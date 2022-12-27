#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.scope import Scope
from base.util.util import Util
import re


class ExecuteLDAPLogin:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

    def login(self, server_address, dn, version, admin_dn, admin_password):
        try:
            self.logger.info("----------------> server_address: " + server_address)
            self.logger.info("----------------> dn: " + dn)
            self.logger.info("----------------> version: " + version)
            self.logger.info("----------------> admin_dn: " + admin_dn)
            self.logger.info("----------------> admin_password: " + admin_password)
            #(result_code, p_out, p_err) = self.util.execute("/bin/bash /usr/share/ahenk/base/registration/scripts/test.sh")
            (result_code, p_out, p_err) = self.util.execute("/bin/bash /usr/share/ahenk/base/registration/scripts/ldap-login.sh {0} {1} {2} {3} {4}".format(server_address, "\'" + dn + "\'", "\'" + admin_dn + "\'", "\'" + admin_password + "\'", version))
            if result_code == 0:
                self.logger.info("Script has run successfully")
            else:
                self.logger.error("Script could not run successfully: " + p_err)

            # pattern for clearing file data from spaces, tabs and newlines
            pattern = re.compile(r'\s+')

            pam_scripts_original_directory_path = "/usr/share/ahenk/pam_scripts_original"

            ldap_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/ldap"
            ldap_original_file_path = "/usr/share/pam-configs/ldap"
            ldap_configured_file_path = "/usr/share/ahenk/plugins/ldap-login/config-files/ldap"

            pam_script_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/pam_script"
            pam_script_original_file_path = "/usr/share/pam-configs/pam_script"
            pam_script_configured_file_path = "/usr/share/ahenk/plugins/ldap-login/config-files/pam_script"

            # create pam_scripts_original directory if not exists
            if not self.util.is_exist(pam_scripts_original_directory_path):
                self.logger.info("Creating {0} directory.".format(pam_scripts_original_directory_path))
                self.util.create_directory(pam_scripts_original_directory_path)

            if self.util.is_exist(ldap_back_up_file_path):
                self.logger.info("Changing {0} with {1}.".format(ldap_original_file_path, ldap_configured_file_path))
                self.util.copy_file(ldap_configured_file_path, ldap_original_file_path)
            else:
                self.logger.info("Backing up {0}".format(ldap_original_file_path))
                self.util.copy_file(ldap_original_file_path, ldap_back_up_file_path)
                self.logger.info(
                    "{0} file is replaced with {1}.".format(ldap_original_file_path, ldap_configured_file_path))
                self.util.copy_file(ldap_configured_file_path, ldap_original_file_path)

            if self.util.is_exist(pam_script_back_up_file_path):
                self.util.copy_file(pam_script_configured_file_path, pam_script_original_file_path)
                self.logger.info(
                    "{0} is replaced with {1}.".format(pam_script_original_file_path, pam_script_configured_file_path))
            else:
                self.logger.info("Backing up {0}".format(pam_script_original_file_path))
                self.util.copy_file(pam_script_original_file_path, pam_script_back_up_file_path)
                self.logger.info("{0} file is replaced with {1}".format(pam_script_original_file_path,
                                                                        pam_script_configured_file_path))
                self.util.copy_file(pam_script_configured_file_path, pam_script_original_file_path)

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

            is_configuration_done_before = False
            if ("passwd:compatldap" not in text):
                file_data = file_data.replace("passwd:         compat", "passwd:         compat ldap")
                is_configuration_done_before = True

            if ("group:compatldap" not in text):
                file_data = file_data.replace("group:          compat", "group:          compat ldap")
                is_configuration_done_before = True

            if ("shadow:compatldap" not in text):
                file_data = file_data.replace("shadow:         compat", "shadow:         compat ldap")
                is_configuration_done_before = True

            if is_configuration_done_before:
                self.logger.info("nsswitch.conf configuration has been completed")
            else:
                self.logger.info("nsswitch.conf is already configured")

            file_ns_switch.close()
            file_ns_switch = open("/etc/nsswitch.conf", 'w')
            file_ns_switch.write(file_data)
            file_ns_switch.close()

            # configure ldap-cache
            self.logger.info("Starting to ldap-cache configurations.")
            result_code, p_out, p_err = self.util.execute("apt-get install nss-updatedb -y")
            if result_code != 0:
                self.logger.error("Error occured while downloading nss-updatedb.")
            else:
                self.logger.info("nss-updatedb downloaded successfully. Configuring /etc/nsswitch.conf.")
                file_ns_switch = open("/etc/nsswitch.conf", 'r')
                file_data = file_ns_switch.read()

                # cleared file data from spaces, tabs and newlines
                text = pattern.sub('', file_data)

                did_configuration_change = False
                if "passwd:compatldap[NOTFOUND=return]db" not in text:
                    file_data = file_data.replace("passwd:         compat ldap",
                                                  "passwd:         compat ldap [NOTFOUND=return] db")
                    did_configuration_change = True

                if "group:compatldap[NOTFOUND=return]db" not in text:
                    file_data = file_data.replace("group:          compat ldap",
                                                  "group:          compat ldap [NOTFOUND=return] db")
                    did_configuration_change = True

                if "gshadow:files" in text and "#gshadow:files" not in text:
                    file_data = file_data.replace("gshadow:        files", "#gshadow:        files")
                    did_configuration_change = True

                if did_configuration_change:
                    self.logger.info("nsswitch.conf configuration has been configured for ldap cache.")
                else:
                    self.logger.info("nsswitch.conf has already been configured for ldap cache.")

                file_ns_switch.close()
                file_ns_switch = open("/etc/nsswitch.conf", 'w')
                file_ns_switch.write(file_data)
                file_ns_switch.close()
                self.util.execute("nss_updatedb ldap")

            # create cron job for ldap cache
            content = "#!/bin/bash\n" \
                      "nss-updatedb ldap"
            nss_update_cron_job_file_path = "/etc/cron.daily/nss-updatedb"
            if self.util.is_exist(nss_update_cron_job_file_path):
                self.logger.info(
                    "{0} exists. File will be deleted and creating new one.".format(nss_update_cron_job_file_path))
                self.util.delete_file(nss_update_cron_job_file_path)
                self.util.create_file(nss_update_cron_job_file_path)
                self.util.write_file(nss_update_cron_job_file_path, content, 'w+')
                self.util.execute("chmod +x " + nss_update_cron_job_file_path)
            else:
                self.logger.info(
                    "{0} doesnt exist. File will be created and content will be written.".format(
                        nss_update_cron_job_file_path))
                self.util.create_file(nss_update_cron_job_file_path)
                self.util.write_file(nss_update_cron_job_file_path, content, 'w+')
                self.util.execute("chmod +x " + nss_update_cron_job_file_path)

            # configure /etc/libnss-ldap.conf
            libnss_ldap_file_path = "/etc/libnss-ldap.conf"
            content = "bind_policy hard" \
                      "\nnss_reconnect_tries 1" \
                      "\nnss_reconnect_sleeptime 1" \
                      "\nnss_reconnect_maxsleeptime 8" \
                      "\nnss_reconnect_maxconntries 2"
            if self.util.is_exist(libnss_ldap_file_path):
                self.logger.info("{0} exists.".format(libnss_ldap_file_path))
                self.util.execute("sed -i '/bind_policy hard/c\\' " + libnss_ldap_file_path)
                self.util.execute("sed -i '/nss_reconnect_tries 1/c\\' " + libnss_ldap_file_path)
                self.util.execute("sed -i '/nss_reconnect_sleeptime 1/c\\' " + libnss_ldap_file_path)
                self.util.execute("sed -i '/nss_reconnect_maxsleeptime 8/c\\' " + libnss_ldap_file_path)
                self.util.execute("sed -i '/nss_reconnect_maxconntries 2/c\\' " + libnss_ldap_file_path)
                self.util.write_file(libnss_ldap_file_path, content, 'a+')
                self.logger.info("Configuration has been made to {0}.".format(libnss_ldap_file_path))

            result_code, p_out, p_err = self.util.execute("apt-get install libnss-db libpam-ccreds libsss-sudo -y")
            if result_code != 0:
                self.logger.error("Error occured while downloading libnss-db libpam-ccreds.")
            else:
                self.logger.error("libnss-db libpam-ccreds are downloaded.")

            # configure sudo-ldap
            sudo_ldap_conf_file_path = "/etc/sudo-ldap.conf"
            content = "sudoers_base ou=Roles," + dn \
                      + "\nBASE " + dn \
                      + "\nURI ldap://" + server_address
            # clean if config is already written
            self.util.execute("sed -i '/BASE /c\\' " + sudo_ldap_conf_file_path)
            self.util.execute("sed -i '/sudoers_base /c\\' " + sudo_ldap_conf_file_path)
            self.util.execute("sed -i '/URI /c\\' " + sudo_ldap_conf_file_path)

            if self.util.is_exist(sudo_ldap_conf_file_path):
                self.logger.info("{0} exists.".format(sudo_ldap_conf_file_path))
                self.util.write_file(sudo_ldap_conf_file_path, content, 'a+')
                self.logger.info("Content is written to {0} successfully.".format(sudo_ldap_conf_file_path))

            # Configure lightdm.service
            # check if 99-pardus-xfce.conf exists if not create
            pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
            if not self.util.is_exist(pardus_xfce_path):
                self.logger.info("99-pardus-xfce.conf does not exist.")
                self.util.create_file(pardus_xfce_path)

                file_lightdm = open(pardus_xfce_path, 'a')
                file_lightdm.write("[Seat:*]\n")
                file_lightdm.write("greeter-hide-users=true")
                file_lightdm.close()
                self.logger.info("lightdm has been configured.")
            else:
                self.logger.info("99-pardus-xfce.conf exists. Delete file and create new one.")
                self.util.delete_file(pardus_xfce_path)
                self.util.create_file(pardus_xfce_path)

                file_lightdm = open(pardus_xfce_path, 'a')
                file_lightdm.write("[Seat:*]")
                file_lightdm.write("greeter-hide-users=true")
                file_lightdm.close()
                self.logger.info("lightdm.conf has been configured.")
            self.util.execute("systemctl restart nscd.service")
            self.util.execute("pam-auth-update --force")
            self.logger.info("LDAP Login operation has been completed.")

            self.logger.info("LDAP Login işlemi başarı ile sağlandı.")
        except Exception as e:
            self.logger.error(str(e))
            self.logger.info("LDAP Login işlemi esnasında hata oluştu.")
            raise Exception('LDAP Ayarları yapılırken hata oluştu. Lütfen ağ bağlantınızı kontrol ediniz. Deponuzun güncel olduğundan emin olunuz.')