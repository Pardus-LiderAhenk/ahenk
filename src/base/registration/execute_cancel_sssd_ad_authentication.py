#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Agah Hulusi ÖZ <enghulusi@gmail.com>

from base.scope import Scope
from base.util.util import Util
import re


class ExecuteCancelSSSDAdAuthentication:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

    def cancel(self):

        # Deleting packages require for AD entegration

        self.util.execute("apt purge realmd sssd sssd-tools adcli krb5-user packagekit samba-common samba-common-bin samba-libs -y")
        self.util.execute("apt autoremove -y")

        # Read information about AD

        if self.util.is_exist("/etc/ahenk/ad_info"):
            file_data = open("/etc/ahenk/ad_info","r")
            ip_address = (file_data.readline())
            host_name = (file_data.readline())
            file_data.close()
            self.logger.info("ad_info dosyasından bilgiler başarılı bir şekilde alındı.")
        else:
            self.logger.error("ad_info dosyasına ulaşılamadı ")


        try:
            if self.util.is_exist("/etc/sssd"):
                self.util.delete_folder("/etc/sssd")
                self.logger.info("SSSD is deleted")
            else:
                self.logger.info("SSSD is not exist")

        except Exception as e:
            self.logger.error("Error while running /etc/SSSD.. Error Message  " + str(e))

        # Re-Configure dhclient.conf deleting AD IP address



        try:
            dhclient_conf_path = "/etc/dhcp/dhclient.conf"
            file_dhclient = open(dhclient_conf_path, 'r')
            file_data = file_dhclient.read()

            if "prepend domain-name-servers {};".format(ip_address) in file_data:
                file_data = file_data.replace(("prepend domain-name-servers {};".format(ip_address)),
                                              "#prepend domain-name-servers 127.0.0.1;")
                self.logger.info("dhclient is reconfigured")
            else:
                self.logger.error("dhclient is'not reconfigured")

            file_dhclient.close()
            file_dhclient = open(dhclient_conf_path, 'w')
            file_dhclient.write(file_data)
            file_dhclient.close()

        except Exception as e:
            self.logger.error("Error while running /dhcp/dhclient.conf.. Error Message  " + str(e))


        # Pattern for clearing file data from spaces, tabs and newlines

        # pattern = re.compile(r'\s+')

#         # Re-Configure nsswitch.conf
#         file_ns_switch = open("/etc/nsswitch.conf", 'r')
#         file_data = file_ns_switch.read()
#
#         # Cleared file data from spaces, tabs and newlines
#         text = pattern.sub('', file_data)
# #BİR BİR BİR BAKKKKKKKKK
#         did_configuration_change = False
#         if "passwd:" in text:
#             file_data = file_data.replace("passwd:         files systemd sss", "passwd:         compat")
#             did_configuration_change = True
#             self.logger.info("passwd:compatss BAŞARILI")
#
#
#         if "group:" in text:
#             file_data = file_data.replace("group:          files systemd sss", "group:          compat")
#             did_configuration_change = True
#             self.logger.info("group:compatss BAŞARILI")
#
#
#
#         if "shadow:" in text:
#             file_data = file_data.replace("shadow:         files sss", "shadow:         compat")
#             did_configuration_change = True
#             self.logger.info("shadow:compatss BAŞARILI")
#
#
#         if "services:" in text:
#             file_data = file_data.replace("services:       db files sss", "services:       db files")
#             did_configuration_change = True
#             self.logger.info("services:compatss BAŞARILI")
#
#
#         if "netgroup:" in text:
#             file_data = file_data.replace("netgroup:       nis sss", "netgroup:       nis")
#             did_configuration_change = True
#             self.logger.info("netgroup:nissss BAŞARILI")
#
#
#         if "sudoers:" in text:
#             file_data = file_data.replace("sudoers:        files sss", " ")
#             did_configuration_change = True
#             self.logger.info("sudoers:filessss BAŞARILI")
#
#
#         if did_configuration_change:
#             self.logger.info("nsswitch.conf configuration has been configured")
#         else:
#             self.logger.info("nsswitch.conf has already been configured")
#
#         file_ns_switch.close()
#         file_ns_switch = open("/etc/nsswitch.conf", 'w')
#         file_ns_switch.write(file_data)
#         file_ns_switch.close()

        # Configure hosts for deleting AD  "IP address" and "AD hostname"
        try:
            hosts_conf_path = "/etc/hosts"
            file_hosts = open(hosts_conf_path, 'r')
            file_data = file_hosts.read()

            if ("{0}    {1}".format(ip_address, host_name)) in file_data:
                file_data = file_data.replace(("{0}    {1}".format(ip_address, host_name)), " ")
                self.logger.info("hosts is configured")
            else:
                self.logger.error("hosts is not configured")
            file_hosts.close()
            file_hosts = open(hosts_conf_path, 'w')
            file_hosts.write(file_data)
            file_hosts.close()

        except Exception as e:
            self.logger.error("Error while running /etc/hosts.. Error Message  " + str(e))

        # Configure common-session for deleting home directories for AD users


        try:
            common_session_conf_path = "/etc/pam.d/common-session"

            file_common_session = open(common_session_conf_path, 'r')
            file_data = file_common_session.read()

            if "session optional pam_mkhomedir.so skel=/etc/skel umask=077" in file_data:
                file_data = file_data.replace("session optional pam_mkhomedir.so skel=/etc/skel umask=077", " ")
                self.logger.info("common-session is configured")
            else:
                self.logger.error("common session is not configured")

            file_common_session.close()
            file_common_session = open(common_session_conf_path, 'w')
            file_common_session.write(file_data)
            file_common_session.close()

        except Exception as e:
            self.logger.error("Error while running /etc/pam.d/common-session.. Error Message  " + str(e))

        # Configure resolv.conf for deleting AD IP address

        resolv_conf_path = "/etc/resolv.conf"

        file_resolv = open(resolv_conf_path, 'r')
        file_data = file_resolv.read()

        if ("nameserver {0}".format(ip_address)) in file_data:
            file_data = file_data.replace(("nameserver {0}".format(ip_address)), "")
            self.logger.info("resolv.conf is configured")
        else:
            self.logger.error("resolv is not configured")

        file_resolv.close()
        file_resolv = open(resolv_conf_path, 'w')
        file_resolv.write(file_data)
        file_resolv.close()

        # Deleting ad_info file


        try:
            if self.util.is_exist("/etc/ahenk/ad_info"):
                (result_code, p_out, p_err) = self.util.execute("rm -rf /etc/ahenk/ad_info")
                if (result_code == 0):
                    self.logger.info("ad_info Başarılı bir şekilde silindi")
                else:
                    self.logger.error("ad_info silinemedi : " + str(p_err))
            else:
                self.logger.error("ad_info dosyasına ulaşılamadı ")

        except Exception as e:
            self.logger.error("Error while running /ad_infoyu SİLERKEN.. Error Message  " + str(e))


        # Configure lightdm.service
        pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
        if self.util.is_exist(pardus_xfce_path):
            self.logger.info("99-pardus-xfce.conf exists. Deleting file.")
            self.util.delete_file(pardus_xfce_path)
            self.util.execute("systemctl restart nscd.service")

        self.logger.info("LDAP Login iptal etme işlemi başarı ile sağlandı.")

