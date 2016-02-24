#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDeamon
from base.logging.AhenkLogger import Logger
from base.Scope import Scope
import sys,logging


class AhenkDeamon(BaseDeamon):
	"""docstring for AhenkDeamon"""

	def run(self):
		globalscope = Scope()
		globalscope.setInstance(globalscope)

		configFilePath='/etc/ahenk/ahenk.conf'
		configfileFolderPath='/etc/ahenk/config.d/'

		#configuration manager must be first load
		configManager = ConfigManager(configFilePath,configfileFolderPath)
		config = configManager.read()
		globalscope.setConfigurationManager(config)

		logger = Logger()
		logger.info("obaraaa")
		globalscope.setLogger(logger)


if __name__ == '__main__':

	pidfilePath='/var/run/ahenk.pid'

	ahenkdeamon = AhenkDeamon(pidfilePath)

	print sys.argv
	if len(sys.argv) == 2:
		if sys.argv[1] == "start":
			print "starting"
			ahenkdeamon.start()
		elif sys.argv[1] == 'stop':
			ahenkdeamon.stop()
		elif sys.argv[1] == 'restart':
			ahenkdeamon.restart()
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
