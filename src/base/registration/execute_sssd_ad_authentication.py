#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Agah Hulusi ÖZ <enghulusi@gmail.com>


from base.scope import Scope
from base.util.util import Util

class ExecuteSSSDAdAuthentication:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

        # self.domain_name = "engerek.local"
        # self.host_name = "liderahenk.engerek.local"
        # self.ip_address = "172.16.103.28"
        # self.password = "Pp123456"


    def authenticate(self, domain_name, host_name, ip_address, password, ad_username):

        # Create and Configure ad_info file
        (result_code, p_out, p_err) = self.util.create_file("/etc/ahenk/ad_info")
        if (result_code == 0):
            self.logger.info("AD INFO başarılı bir şekilde oluşturuldu")
            # Configure ad_info for deregisteration info
            default_ad_info_path = "/etc/ahenk/ad_info"
            file_default_ad_info = open(default_ad_info_path, 'r')
            file_data = file_default_ad_info.read()

            file_data = file_data + ("{}".format(ip_address)) + "\n" + ("{}".format(host_name)) + "\n" + (
                "{}".format(domain_name)) + "\n" + ("{}".format(ad_username))
            self.logger.info("/etc/ahenk/ad_info bilgiler girildi.")
            file_default_ad_info.close()
            file_default_ad_info = open(default_ad_info_path, 'w')
            file_default_ad_info.write(file_data)
            file_default_ad_info.close()
        else:
            self.logger.error("ad_info oluşturma komutu başarısız : " + str(p_err))

        self.logger.info("Authenticate starting....")
        # Configure /etc/dhcp/dhclient.conf
        dhclient_conf_path = "/etc/dhcp/dhclient.conf"
        dhc_conf = self.util.read_file_by_line(dhclient_conf_path, "r")
        dhc_conf_temp = open(dhclient_conf_path, 'w')

        for lines in dhc_conf:
            if (lines == "#prepend domain-name-servers 127.0.0.1;\n"):
                lines = lines.replace(lines, ("prepend domain-name-servers {};\n".format(ip_address)))
            dhc_conf_temp.write(lines)
        dhc_conf_temp.close()

        file_default_dhcp = open(dhclient_conf_path, 'r')
        file_data = file_default_dhcp.read()

        if ("prepend domain-name-servers {};\n".format(ip_address)) not in file_data:
            file_data = file_data + "\n" + ("prepend domain-name-servers {};".format(ip_address))

        file_default_dhcp.close()
        file_default_dhcp = open(dhclient_conf_path, 'w')
        file_default_dhcp.write(file_data)
        file_default_dhcp.close()


        # Configure /etc/resolv.conf
        resolve_conf_path = "/etc/resolv.conf"
        resolve_conf = self.util.read_file_by_line(resolve_conf_path, "r")
        resolve_conf_temp = open(resolve_conf_path, 'w')

        for lines in resolve_conf:
            if (lines == ("nameserver {}\n".format(ip_address))):
                continue
            lines = lines.replace(lines, ("#" + lines))
            resolve_conf_temp.write(lines)
        resolve_conf_temp.close()

        file_default_resolve = open(resolve_conf_path, 'r')
        file_data = file_default_resolve.read()

        if ("nameserver {}\n".format(ip_address)) not in file_data:
            file_data = file_data + "\n" + ("nameserver {}\n".format(ip_address))
            self.logger.info("/etc/resolv.conf is configured")

        file_default_resolve.close()
        file_default_resolve = open(resolve_conf_path, 'w')
        file_default_resolve.write(file_data)
        file_default_resolve.close()


        # Configure /etc/hosts
        host_path = "/etc/hosts"
        file_default_hosts = open(host_path, 'r')
        file_data = file_default_hosts.read()

        if ("{0}    {1}".format(ip_address, host_name)) not in file_data:
            file_data = file_data + "\n" + ("{0}    {1}".format(ip_address, host_name))
            self.logger.info("/etc/hosts is configured")

        file_default_hosts.close()
        file_default_hosts = open(host_path, 'w')
        file_default_hosts.write(file_data)
        file_default_hosts.close()


        # Execute the script that required for "samba-common" and "krb5"
        (result_code, p_out, p_err) = self.util.execute("/bin/bash /usr/share/ahenk/base/registration/scripts/ad.sh {0} {1}".format(domain_name.upper(),host_name))

        if(result_code == 0):
            self.logger.info("Script başarılı bir  şekilde çalıştırıldı.")
        else:
            self.logger.error("Script başarısız oldu : " + str(p_err))

        # Installation of required packages
        (result_code, p_out, p_err) = self.util.execute("sudo apt-get -y install realmd sssd sssd-tools adcli packagekit samba-common-bin samba-libs")
        if (result_code == 0):
            self.logger.info("İndirmeler Başarılı")
        else:
            self.logger.error("İndirmeler Başarısız : " + str(p_err))


        # Configure pam.d/common-session
        pamd_common_session_path = "/etc/pam.d/common-session"
        file_default_pam = open(pamd_common_session_path, 'r')
        file_data = file_default_pam.read()

        if "session optional        pam_mkhomedir.so skel=/etc/skel umask=077" not in file_data:
            file_data = file_data + "\n" + "session optional        pam_mkhomedir.so skel=/etc/skel umask=077"
            self.logger.info("/etc/pam.d/common-session is configured")

        file_default_pam.close()
        file_default_pam = open(pamd_common_session_path, 'w')
        file_default_pam.write(file_data)
        file_default_pam.close()

        # Execute the commands that require for join Domain
        (result_code, p_out, p_err) = self.util.execute("realm discover {}".format(domain_name.upper()))
        if (result_code == 0):
            self.logger.info("Realm Discover komutu başarılı")
        else:
            self.logger.error("Realm Discover komutu başarısız : " + str(p_err))

        (result_code, p_out, p_err) = self.util.execute("echo \"{0}\" | realm join --user={1} {2}".format(password, ad_username, domain_name.upper()))
        if (result_code == 0):
            self.logger.info("Realm Join komutu başarılı")
        else:
            self.logger.error("Realm Join komutu başarısız : " + str(p_err))

        # Configure sssd template
        sssd_config_template_path = "/usr/share/ahenk/base/registration/config-files/sssd_ad.conf"
        sssd_config_folder_path = "/etc/sssd"
        sssd_config_file_path = "/etc/sssd/sssd.conf"

        if not self.util.is_exist(sssd_config_folder_path):
            self.util.create_directory(sssd_config_folder_path)
            self.logger.info("{0} folder is created".format(sssd_config_folder_path))

        if self.util.is_exist(sssd_config_file_path):
            self.util.delete_file(sssd_config_file_path)
            self.logger.info("delete sssd org conf")

        self.util.copy_file(sssd_config_template_path, sssd_config_folder_path)
        self.logger.info("{0} config file is copied under {1}".format(sssd_config_template_path, sssd_config_folder_path))
        self.util.rename_file("/etc/sssd/sssd_ad.conf", "/etc/sssd/sssd.conf")

        # Configure sssd.conf
        file_sssd = open(sssd_config_file_path, 'r')
        file_data = file_sssd.read()

        file_data = file_data.replace("###domains###", "domains = {}".format(domain_name))
        file_data = file_data.replace("###[domain/###", "[domain/{}]".format(domain_name))
        file_data = file_data.replace("###ad_domain###", "ad_domain = {}".format(domain_name))
        file_data = file_data.replace("###krb5_realm###", "krb5_realm = {}".format(domain_name.upper()))

        file_sssd.close()
        file_sssd = open(sssd_config_file_path, 'w')
        file_sssd.write(file_data)
        file_sssd.close()





        # Arrangement of chmod as 600 for sssd.conf
        (result_code, p_out, p_err) = self.util.execute("chmod 600 {}".format(sssd_config_file_path))
        if(result_code == 0):
            self.logger.info("Chmod komutu başarılı bir şekilde çalıştırıldı")
        else:
            self.logger.error("Chmod komutu başarısız : " + str(p_err))

        # Configure sssd for language environment
        default_sssd_path = "/etc/default/sssd"
        file_default_sssd = open(default_sssd_path, 'r')
        file_data = file_default_sssd.read()

        if not self.util.is_exist(default_sssd_path):
            self.util.create_directory(default_sssd_path)
            self.logger.info("{0} folder is created".format(default_sssd_path))

        if self.util.is_exist(default_sssd_path):
            self.util.delete_file(default_sssd_path)
            self.logger.info("delete sssd org conf")

        if "LC_ALL=\"tr_CY.UTF-8\"" not in file_data :
            file_data = file_data + "\n" + "LC_ALL=\"tr_CY.UTF-8\""
            self.logger.info("/etc/default/sssd is configured")

        file_default_sssd.close()
        file_default_sssd = open(default_sssd_path, 'w')
        file_default_sssd.write(file_data)
        file_default_sssd.close()

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
        # self.util.execute("pam-auth-update --force")
        self.logger.info("AD Login operation has been completed.")

        self.logger.info("AD Login işlemi başarı ile sağlandı.")
        return True

