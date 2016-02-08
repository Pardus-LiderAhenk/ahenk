#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDeamon
from base.logging.AhenkLogger import Logger
import sys,logging


class AhenkDeamon(BaseDeamon):
	"""docstring for AhenkDeamon"""
	def __init__(self, arg):
		super(AhenkDeamon, self).__init__()
		self.arg = arg

if __name__ == '__main__':

	configFilePath='/etc/ahenk/ahenk.conf'
	configfileFolderPath='/etc/ahenk/config.d/'
	pidfilePath='/var/run/ahenk.pid'

	configManager = ConfigManager(configFilePath,configfileFolderPath)
	config = configManager.read()

	logger = Logger('/tmp/ahenk.log',logging.DEBUG)
	logger.info("obaraaa")

"""
	deamon = AhenkDeamon(pidfilePath)
	
	if len(sys.argv) == 2:
		if sys.argv[1] == "start":
			deamon.start()
		elif sys.argv[1] == 'stop':
			deamon.stop()
		elif sys.argv[1] == 'restart':
			deamon.restart()
		elif sys.argv[1] == 'status':
			# print status
			pass
		else:
			print 'Unknown command. Usage : %s start|stop|restart|status' % sys.argv[0]
			sys.exit(2)
		sys.exit(0)
	else:
		print 'Usage : %s start|stop|restart|status' % sys.argv[0]
		sys.exit(2)
"""