#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import ConfigParser,os
from os import listdir
from os.path import isfile, join
from ConfigParser import SafeConfigParser

class ConfigManager(object):
	"""
		This class written for configuration file management of ahenk and ahenk plugins
		Sample ahenk configuration file path /etc/ahenk/ahenk.conf and sample ahenk plugins configuration folder path /etc/ahenk/config.d/
		Usage: Takes two argument, - both of them are optional - one of the is a configuration file path the other one 
		is configuration files folder path
	"""
	def __init__(self, configurationFilePath=None, configurationFolderPath=None):
		super(ConfigManager, self).__init__()
		self.configurationFilePath = configurationFilePath
		self.configurationFolderPath = configurationFolderPath


	def read(self):
		configFiles = []

		# Check if given ahenk configuration file exists
		# If file exists add it to configFiles array.
		# TODO must write config file validater !!
		if self.configurationFilePath:
			if os.path.exists(self.configurationFilePath):
				configFiles.append(self.configurationFilePath)

		if self.configurationFolderPath and os.path.exists(self.configurationFolderPath):
			 files = [f for f in listdir(self.configurationFolderPath) if isfile(join(self.configurationFolderPath, f))]
			 for f in files:
			 	configFiles.append(join(self.configurationFolderPath, f))

		parser = SafeConfigParser()
		configValues = parser.read(configFiles)

		return parser