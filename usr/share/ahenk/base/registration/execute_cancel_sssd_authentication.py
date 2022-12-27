#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Hasan Kara <h.kara27@gmail.com>

from base.scope import Scope
from base.util.util import Util
import re


class ExecuteCancelSSSDAuthentication:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

    def cancel(self):
        self.util.execute("apt purge libpam-sss sssd-common libsss-sudo -y")
        self.util.execute("apt autoremove -y")

        if self.util.is_exist("/etc/sssd"):
            self.util.delete_folder("/etc/sssd")

        # pattern for clearing file data from spaces, tabs and newlines
        pattern = re.compile(r'\s+')

        # Configure nsswitch.conf
        # file_ns_switch = open("/etc/nsswitch.conf", 'r')
        # file_data = file_ns_switch.read()
        #
        # # cleared file data from spaces, tabs and newlines
        # text = pattern.sub('', file_data)

        # did_configuration_change = False
        # if "passwd:compatsss" in text:
        #     file_data = file_data.replace("passwd:         compat sss", "passwd:         compat")
        #     did_configuration_change = True
        #
        # if "group:compatsss" in text:
        #     file_data = file_data.replace("group:          compat sss", "group:          compat")
        #     did_configuration_change = True
        #
        # if "shadow:compatsss" in text:
        #     file_data = file_data.replace("shadow:         compat sss", "shadow:         compat")
        #     did_configuration_change = True
        #
        # if "services:dbfilessss" in text:
        #     file_data = file_data.replace("services:       db files sss", "services:       db files")
        #     did_configuration_change = True
        #
        # if "netgroup:nissss" in text:
        #     file_data = file_data.replace("netgroup:       nis sss", "netgroup:       nis")
        #     did_configuration_change = True
        #
        # if "sudoers:filessss" in text:
        #     file_data = file_data.replace("sudoers:        files sss", "")
        #     did_configuration_change = True
        #
        # if did_configuration_change:
        #     self.logger.info("nsswitch.conf configuration has been configured")
        # else:
        #     self.logger.info("nsswitch.conf has already been configured")

        # file_ns_switch.close()
        # file_ns_switch = open("/etc/nsswitch.conf", 'w')
        # file_ns_switch.write(file_data)
        # file_ns_switch.close()

        common_session_conf_path = "/etc/pam.d/common-session"

        # configure common-session for creating home directories for ldap users
        file_common_session = open(common_session_conf_path, 'r')
        file_data = file_common_session.read()

        if "session optional        pam_mkhomedir.so skel=/etc/skel umask=077" in file_data:
            file_data = file_data.replace("session optional        pam_mkhomedir.so skel=/etc/skel umask=077", "")
            self.logger.info("common-session is configured")

        file_common_session.close()
        file_common_session = open(common_session_conf_path, 'w')
        file_common_session.write(file_data)
        file_common_session.close()

        self.util.execute("systemctl restart nscd.service")
        self.logger.info("LDAP Login iptal etme işlemi başarı ile sağlandı.")

