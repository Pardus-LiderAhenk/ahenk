#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import os
from configparser import SafeConfigParser
from os import listdir
from os.path import isfile, join


class ConfigManager(object):
    """
        This class written for configuration file management of ahenk and ahenk plugins
        Sample ahenk configuration file path /etc/ahenk/ahenk.conf and sample ahenk plugins configuration folder path /etc/ahenk/config.d/
        Usage: Takes two argument, - both of them are optional - one of the is a configuration file path the other one
        is configuration files folder path
    """

    def __init__(self, configuration_file_path=None, configuration_folder_path=None):
        self.configurationFilePath = configuration_file_path
        self.configurationFolderPath = configuration_folder_path

    def read(self):
        config_files = []

        # Check if given ahenk configuration file exists
        # If file exists add it to configFiles array.
        # TODO must write config file validater !!
        if self.configurationFilePath:
            if os.path.exists(self.configurationFilePath):
                config_files.append(self.configurationFilePath)

        if self.configurationFolderPath and os.path.exists(self.configurationFolderPath):
            files = [f for f in listdir(self.configurationFolderPath) if isfile(join(self.configurationFolderPath, f))]
            for f in files:
                config_files.append(join(self.configurationFolderPath, f))

        parser = SafeConfigParser()
        configValues = parser.read(config_files)

        return parser
