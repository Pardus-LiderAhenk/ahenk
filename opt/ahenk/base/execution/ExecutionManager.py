#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import sys
import logging,subprocess
import logging.config
from base.Scope import Scope

class ExecutionManager(object):
	"""docstring for FileTransferManager"""

	def __init__(self):
		super(ExecutionManager, self).__init__()

		scope = Scope.getInstance()
		self.config_manager = scope.getConfigurationManager()
		self.event_manager = scope.getEventManager()

		self.event_manager.register_event('EXECUTE_TASK',self.execute_task)
		self.event_manager.register_event('EXECUTE_SCRIPT',self.execute_script)
		self.event_manager.register_event('SEND_FILE',self.send_file)

	def execute_task(self,arg):
		print("execute_task")

	def execute_script(self,arg):
		print("execute_script")
		j = json.loads(arg)
		msg_id =str(j['id']).lower()
		file_name =str(j['filePath']).lower()
		time_stamp=str(j['timestamp']).lower()
		subprocess.call("/bin/sh "+self.conf_manager.get('CONNECTION', 'receivefileparam')+file_name, shell=True)

	#need to move somewhere else
	def send_file(self,arg):
		print("send_file")
		j = json.loads(arg)
		msg_id =str(j['id']).lower()
		file_path =str(j['filePath']).lower()
		time_stamp=str(j['timestamp']).lower()

		message_sender=MessageSender(None,file_path)
		message_sender.connect_to_server()
