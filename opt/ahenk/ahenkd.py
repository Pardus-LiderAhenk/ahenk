#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDeamon
from base.logger.AhenkLogger import AhenkLogger
from base.Scope import Scope
#from base.messaging.Messaging import Messaging
import sys,logging


class AhenkDeamon(BaseDeamon):
	"""docstring for AhenkDeamon"""
	globalscope=None
	def __init__(self, arg):
		super(AhenkDeamon, self).__init__()
		self.arg = arg
		global globalscope
		globalscope=Scope()

	@staticmethod
	def scope():
		return globalscope

	def run(self):
		global globalscope
		configFilePath='/etc/ahenk/ahenk.conf'
		configfileFolderPath='/etc/ahenk/config.d/'

		#configuration manager must be first load
		configManager = ConfigManager(configFilePath,configfileFolderPath)
		config = configManager.read()
		globalscope.setConfigurationManager(config)

		#logger = AhenkLogger()
		#logger.info("obaraaa")
		#globalscope.setLogger(logger)

		#messaging=Messaging()
		#messaging.connectToServer()


if __name__ == '__main__':
	print "hello"
	print sys.path
"""
	pidfilePath='/var/run/ahenk.pid'

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
