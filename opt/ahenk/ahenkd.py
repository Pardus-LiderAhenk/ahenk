#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDaemon
from base.logger.AhenkLogger import Logger
from base.Scope import Scope
from base.messaging.MessageReceiver import MessageReceiver
from base.messaging.MessageSender import MessageSender
from base.registration.Registration import Registration
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

		registration=Registration()
		globalscope.setRegistration(registration)

		if registration.is_registered() is False:
			message_sender=MessageSender(registration.get_registration_request_message())
			message_sender.connect_to_server()
			registration.confirm_registration()

		""""
		message_receiver = MessageReceiver()
		rec_process = Process(target=message_receiver.connect_to_server)
		rec_process.start()
		"""

		"""
		else:


		"""
		"""
		#TODO send register message according to register status
		print("sending registration message")
		message_sender = MessageSender(registration.get_registration_message())
		message_sender.connect_to_server()
		print("registration message were sent")
		#TODO add sender to scope

		message_receiver = MessageReceiver()
		rec_process = Process(target=message_receiver.connect_to_server)
		rec_process.start()
		print("receiver online")
		#set parameters which will use for message sending
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
