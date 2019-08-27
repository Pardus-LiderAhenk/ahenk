#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Tuncay Çolak <tuncay.colak@tubitak.gov.tr> <tncyclk05@gmail.com>
# Author: Hasan Kara <h.kara27@gmail.com>

# Default Policy for users

from base.scope import Scope
from base.util.util import Util
import xml.etree.ElementTree as ET

class DefaultPolicy:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.util = Util()

    ## default firefox policy for user
    def default_firefox_policy(self, username):

        self.logger.info("if mozilla profile is not created run firefox to create profile for user: " + username)
        if not Util.is_exist("/home/" + username + "/.mozilla/"):
            self.logger.info("firefox profile does not exist. Check autostart file.")
            if not Util.is_exist("/home/" + username + "/.config/autostart/"):
                self.logger.info(".config/autostart folder does not exist. Creating folder.")
                Util.create_directory("/home/" + username + "/.config/autostart/")
            else:
                self.logger.info(".config/autostart folder exists.")
                self.logger.info(
                    "Checking if firefox-esr-autostart-for-profile.desktop autorun file exists.")

            if not Util.is_exist(
                    "/home/" + username + "/.config/autostart/firefox-esr-autostart-for-profile.desktop"):
                self.logger.info(
                    "firefox-esr-autostart-for-profile.desktop autorun file does not exists. Creating file.")
                Util.create_file(
                    "/home/" + username + "/.config/autostart/firefox-esr-autostart-for-profile.desktop")
                content = "[Desktop Entry]\n\n" \
                          "Type=Application\n\n" \
                          "Exec=firefox-esr www.liderahenk.org"
                Util.write_file(
                    "/home/" + username + "/.config/autostart/firefox-esr-autostart-for-profile.desktop",
                    content)
                self.logger.info(
                    "Autorun config is written to firefox-esr-autostart-for-profile.desktop.")
            else:
                self.logger.info("firefox-esr-autostart-for-profile.desktop exists")
        else:
            self.logger.info(".mozilla firefox profile path exists. Delete autorun file.")
            Util.delete_file(
                "/home/" + username + "/.config/autostart/firefox-esr-autostart-for-profile.desktop")

    ## disabled update package notify for user
    def disable_update_package_notify(self, username):

        xfce4_notify_template_path = "/usr/share/ahenk/base/default_policy/config-files/xfce4-notifyd.xml"

        fileName = "/home/{0}/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-notifyd.xml".format(username)

        if not self.util.is_exist(fileName):
            ## if configuration file does not exist will be create  /home/{username}/.config/xfce4/xfconf/xfce-perchannel-xml/
            self.logger.info("Configuration file does not exist")
            self.util.create_directory("/home/{0}/.config/xfce4/xfconf/xfce-perchannel-xml/".format(username))
            self.logger.info("Created directory /home/{0}/.config/xfce4/xfconf/xfce-perchannel-xml/".format(username))
            self.util.copy_file(xfce4_notify_template_path, "/home/{0}/.config/xfce4/xfconf/xfce-perchannel-xml/".format(username))
            self.logger.info("Copy xfce4-notifyd.xml template file")
            gid = self.util.file_group("/home/{0}".format(username))
            cmd = "chown -R {0}:{1} /home/{0}/.config".format(username, gid)
            self.util.execute(cmd)
            self.logger.info("Set permissons for /home/{0}.config directory".format(username))

            self.notifyd_xml_parser(username)
        else:
            self.logger.info("Configuration file exist")
            self.notifyd_xml_parser(username)

        pk_update_icon_file = "/etc/xdg/autostart/pk-update-icon.desktop"
        if self.util.is_exist(pk_update_icon_file):
            self.logger.info("{0} file exists".format(pk_update_icon_file))
            self.util.rename_file(pk_update_icon_file, pk_update_icon_file+".ahenk")
            self.logger.info("Renamed from {0} to {0}.ahenk".format(pk_update_icon_file))
            self.logger.info("Disabled autostart for pk-update-icon")

        else:
            self.logger.info("File not found")

        self.logger.info("Disable notifications if there is a package update notification for user: " + username)

    def notifyd_xml_parser(self, username):

        fileName = "/home/{0}/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-notifyd.xml".format(username)
        tree = ET.parse(fileName)
        root = tree.getroot()
        app_name_for_blocking = "pk-update-icon"
        element = root.find("./property/[@name='applications']")
        if element is None:
            self.logger.info("applications element could not be found.")
        else:
            element = root.find("./property/property[@name='muted_applications']")
            if element is None:
                self.logger.info("muted_applications element could not be found.")
                self.logger.info("adding muted_applications element to applications tag.")
                element = root.find("./property/[@name='applications']")
                new_element = ET.SubElement(element, 'property')
                new_element.attrib["name"] = 'muted_applications'
                new_element.attrib["type"] = 'array'
                tree.write(fileName)
            else:
                self.logger.info("muted_applications tag exists.")

            self.logger.info("checking if '" + app_name_for_blocking + "' exists in muted_applications tag.")
            element = root.find(
                "./property/property[@name='muted_applications']/value[@value='{0}']".format(app_name_for_blocking))
            if element is None:
                self.logger.info("'" + app_name_for_blocking + "' is not found in muted_applications element.")
                self.logger.info("'" + app_name_for_blocking + "' will be added to muted_applications tag.")
                element = root.find("./property/property[@name='muted_applications']")
                new_element = ET.SubElement(element, 'value')
                new_element.attrib["type"] = 'string'
                new_element.attrib["value"] = app_name_for_blocking
                tree.write(fileName)
            else:
                self.logger.info("'" + app_name_for_blocking + "' is already added to muted_applications tag.")