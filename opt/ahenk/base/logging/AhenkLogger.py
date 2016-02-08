#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

import logging
import logging.config

class Logger(object):
	"""docstring for Logger"""
	def __init__(self, logfilepath, loglevel):
		super(Logger, self).__init__()
		logging.config.fileConfig('logging.conf')
		self.logger = logging.basicConfig(filename=logfilepath,level=loglevel)
	

	def info(self,logstring):
		self.logger.info(logstring)

	def warning(self,logstring):
		self.logger.warning(logstring)