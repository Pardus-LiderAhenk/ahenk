#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Agah Hulusi ÖZ <enghulusi@gmail.com>

from base.scope import Scope
from base.util.util import Util
from base.system.system import System
import re


class ExecuteCancelSSSDAdAuthentication:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()
        self.system = System()
        self.ad_info_path = "/etc/ahenk/ad_info"

    def cancel(self):
        try:

            # Read information about AD
            if self.util.is_exist(self.ad_info_path):
                file_data = self.util.read_file_by_line(self.ad_info_path)
                self.ip_list = file_data[0].strip("\n").replace("[", "").replace("]", "")
                self.host_list = file_data[1].strip("\n").replace("[", "").replace("]", "")
                self.domain_name = file_data[2].strip("\n")

                self.ip_address = self.ip_list.split(", ")
                self.host_name = self.host_list.split(", ")

                self.ip_address[0] = self.ip_address[0].replace("'", "")
                self.host_name[0] = self.host_name[0].replace("'", "")

                self.logger.info(self.ip_address)
                self.logger.info(self.host_name)
                self.logger.info(self.domain_name)
                self.logger.info(self.ip_list)
                self.logger.info(self.host_list)

                self.logger.info("Information read successfully from ad_info.")
            else:
                self.logger.error("ad_info file not found")

            # Leave old domain
            (result_code, p_out, p_err) = self.util.execute("realm leave ")
            if (result_code == 0):
                self.logger.info("Realm Leave komutu başarılı")
            else:
                self.logger.error("Realm Leave komutu başarısız : " + str(p_err))

            # Re-Configure dhclient.conf deleting AD IP address
            dhclient_conf_path = "/etc/dhcp/dhclient.conf"
            file_dhclient = open(dhclient_conf_path, 'r')
            file_data = file_dhclient.read()

            if "prepend domain-name-servers {};".format(self.ip_address[0]) in file_data:
                file_data = file_data.replace(("prepend domain-name-servers {};".format(self.ip_address[0])),
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

            for ip, host in zip(self.ip_address, self.host_name):
                ip = ip.replace("'", "")
                host = host.replace("'", "")
                if ("{0}       {1} {2}".format(ip, host, self.domain_name)) in file_data:
                    file_data = file_data.replace(("{0}       {1} {2}".format(ip, host, self.domain_name)), " ")

            file_hosts.close()
            file_hosts = open(hosts_conf_path, 'w')
            file_hosts.write(file_data)
            file_hosts.close()

            # Configure common-session for deleting home directories for AD users
            common_session_conf_path = "/etc/pam.d/common-session"
            file_common_session = open(common_session_conf_path, 'r')
            file_data = file_common_session.read()

            if "session optional        pam_mkhomedir.so skel=/etc/skel umask=077" in file_data:
                file_data = file_data.replace("session optional        pam_mkhomedir.so skel=/etc/skel umask=077", " ")
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

            if ("nameserver {0}".format(self.ip_address[0])) in file_data:
                file_data = file_data.replace(("nameserver {0}".format(self.ip_address[0])), "")
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

            self.logger.info("AD Login iptal etme işlemi başarı ile sağlandı.")
            return True

        except Exception as e:
            self.logger.error(str(e))
            self.logger.info("AD Login İptal etme işlemi esnasında hata oluştu.")
            return False
