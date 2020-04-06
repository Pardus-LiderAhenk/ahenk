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
        self.ad_info_path = "/etc/ahenk/ad_info"

    def cancel(self):
        try:
            # Deleting packages require for AD entegration
            self.util.execute(
                "apt purge realmd sssd sssd-tools adcli krb5-user packagekit samba-common samba-common-bin samba-libs -y")
            self.util.execute("apt autoremove -y")

            # Read information about AD
            if self.util.is_exist(self.ad_info_path):
                file_data = self.util.read_file_by_line(self.ad_info_path)
                self.ip_address = file_data[0].strip("\n")
                self.host_name = file_data[1].strip("\n")
                self.logger.info(self.ip_address)
                self.logger.info(self.host_name)
                self.logger.info("Information read successfully from ad_info.")
            else:
                self.logger.error("ad_info file not found")

            if self.util.is_exist("/etc/sssd"):
                # self.util.delete_folder("/etc/sssd")
                self.logger.info("SSSD is deleted")
            else:
                self.logger.info("SSSD is not exist")

            # Re-Configure dhclient.conf deleting AD IP address
            dhclient_conf_path = "/etc/dhcp/dhclient.conf"
            file_dhclient = open(dhclient_conf_path, 'r')
            file_data = file_dhclient.read()

            if "prepend domain-name-servers {};".format(self.ip_address) in file_data:
                file_data = file_data.replace(("prepend domain-name-servers {};".format(self.ip_address)),
                                              "#prepend domain-name-servers 127.0.0.1;")
                self.logger.info("dhclient is reconfigured")
            else:
                self.logger.error("dhclient is'not reconfigured")

            file_dhclient.close()
            file_dhclient = open(dhclient_conf_path, 'w')
            file_dhclient.write(file_data)
            file_dhclient.close()

            # Configure hosts for deleting AD  "IP address" and "AD hostname"
            hosts_conf_path = "/etc/hosts"
            file_hosts = open(hosts_conf_path, 'r')
            file_data = file_hosts.read()

            if ("{0}    {1}".format(self.ip_address, self.host_name)) in file_data:
                file_data = file_data.replace(("{0}    {1}".format(self.ip_address, self.host_name)), " ")
                self.logger.info("hosts is configured")
            else:
                self.logger.error("hosts is not configured")
            file_hosts.close()
            file_hosts = open(hosts_conf_path, 'w')
            file_hosts.write(file_data)
            file_hosts.close()

            # Configure common-session for deleting home directories for AD users
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

            # Configure resolv.conf for deleting AD IP address
            resolv_conf_path = "/etc/resolv.conf"
            file_resolv = open(resolv_conf_path, 'r')
            file_data = file_resolv.read()

            if ("nameserver {0}".format(self.ip_address)) in file_data:
                file_data = file_data.replace(("nameserver {0}".format(self.ip_address)), "")
                self.logger.info("resolv.conf is configured")
            else:
                self.logger.error("resolv is not configured")

            file_resolv.close()
            file_resolv = open(resolv_conf_path, 'w')
            file_resolv.write(file_data)
            file_resolv.close()

            # Deleting ad_info file
            if self.util.is_exist(self.ad_info_path):
                self.util.delete_file(self.ad_info_path)
                self.logger.info("Deleted ad_info file")
            else:
                self.logger.error("ad_info file not found")

            # Configure lightdm.service
            pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
            if self.util.is_exist(pardus_xfce_path):
                self.logger.info("99-pardus-xfce.conf exists. Deleting file.")
                self.util.delete_file(pardus_xfce_path)
                self.util.execute("systemctl restart nscd.service")
            else:
                self.logger.info("99-pardus-xfce.conf not found")

            self.logger.info("AD Login iptal etme işlemi başarı ile sağlandı.")
            return True

        except Exception as e:
            self.logger.error(str(e))
            self.logger.info("AD Login İptal etme işlemi esnasında hata oluştu.")
            return False
