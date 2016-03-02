#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDaemon
from base.logger.AhenkLogger import Logger
from base.Scope import Scope
from base.messaging.Messaging import Messaging
from base.messaging.MessageReceiver import MessageReceiver
from base.messaging.MessageSender import MessageSender
from base.registration.Registration import Registration
from multiprocessing import Process
from threading import Thread
import sys,logging
import time


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

		logger = Logger()
		logger.debug("[AhenkDeamon]logging")
		globalscope.setLogger(logger)

		registration = Registration()
		registration.register()

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
