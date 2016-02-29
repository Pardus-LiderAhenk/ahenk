#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import sys
sys.path.append('../..')
import logging
import logging.config
from base.Scope import Scope

class AhenkLogger(object):
	"""docstring for Logger"""
	def __init__(self):
		super(Logger, self).__init__()
		scope = Scope.getInstance()
		configManager = scope.getConfigurationManager()

		logging.config.fileConfig(configManager.get('BASE','logConfigurationFilePath'))
		self.logger = logging.getLogger()

	def getLogger(self):
		return self.logger

	def info(self,logstring):
		self.logger.info(logstring)

	def warning(self,logstring):
		self.logger.warning(logstring)

	def error(self,logstring):
		self.logger.error(logstring)

	def debug(self,logstring):
		self.logger.debug(logstring)
