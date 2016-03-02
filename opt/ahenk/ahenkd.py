#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDaemon
from base.logger.AhenkLogger import Logger
from base.Scope import Scope
from base.messaging.Messaging import Messaging
from base.messaging.MessageResponseQueue import MessageResponseQueue
from base.plugin.PluginManager import PluginManager
from base.task.TaskManager import TaskManager
from multiprocessing import Process
from threading import Thread
import sys,logging,queue,time


class AhenkDeamon(BaseDaemon):
	"""docstring for AhenkDeamon"""

	def run(self):
		print ("merhaba dunya")
		globalscope = Scope()
		globalscope.setInstance(globalscope)

		configFilePath='/etc/ahenk/ahenk.conf'
		configfileFolderPath='/etc/ahenk/config.d/'

		#configuration manager must be first load
		configManager = ConfigManager(configFilePath,configfileFolderPath)
		config = configManager.read()
		globalscope.setConfigurationManager(config)

		# Logger must be second
		logger = Logger()
		logger.info("this is info log")
		globalscope.setLogger(logger)

		pluginManager = PluginManager()
		pluginManager.loadPlugins()
		globalscope.setPluginManager(pluginManager)

		taskManger = TaskManager()
		globalscope.setTaskManager(taskManger)

		# add services after this line

		"""
			xmpp = Messaging()
			print("xmpp is created")
			p = Process(target=xmpp.connect_to_server)
			print("Process thread starting")
			p.start()
			print("Process tread started")
			print("waiting 5sn ")
			time.sleep(5)
			print("sleep is over ")
			xmpp.send_direct_message("asdasdas")# not working ->connection error
		"""

		"""
			this is must be created after message services
			responseQueue = queue.Queue()
			messageResponseQueue = MessageResponseQueue(responseQueue)
			messageResponseQueue.setDaemon(True)
			messageResponseQueue.start()
			globalscope.setResponseQueue(responseQueue)
		"""

if __name__ == '__main__':

	pidfilePath='/var/run/ahenk.pid'

	ahenkdaemon = AhenkDeamon(pidfilePath)

	print (sys.argv)

	if len(sys.argv) == 2:
		if sys.argv[1] == "start":
			print ("starting")
			ahenkdaemon.run()
			#print (ahenkdaemon.get_pid())
		elif sys.argv[1] == 'stop':
			ahenkdaemon.stop()
		elif sys.argv[1] == 'restart':
			ahenkdaemon.restart()
		elif sys.argv[1] == 'status':
			# print (status)
			pass
		else:
			print ('Unknown command. Usage : %s start|stop|restart|status' % sys.argv[0])
			sys.exit(2)
		sys.exit(0)
	else:
		print ('Usage : %s start|stop|restart|status' % sys.argv[0])
		sys.exit(2)
