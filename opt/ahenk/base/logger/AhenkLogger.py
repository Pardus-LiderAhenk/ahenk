#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
import sys
import logging
import logging.config
sys.path.insert(0,'/home/ismail/devzone/workspace/lider-ahenk/ahenk/opt/ahenk/')
#import ahenkd

class AhenkLogger(object):
	"""docstring for Logger"""
	def __init__(self):
		super(Logger, self).__init__()
		scope = ahenkd.AhenkDeamon.scope()
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


if __name__ == '__main__':
	print "hello"
	print sys.path
