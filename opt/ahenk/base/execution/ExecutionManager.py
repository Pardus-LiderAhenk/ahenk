#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import subprocess
from base.Scope import Scope
from base.messaging.MessageSender import MessageSender
import hashlib,json,os,stat,shutil

class ExecutionManager(object):
    """docstring for FileTransferManager"""

    def __init__(self):
        super(ExecutionManager, self).__init__()

        scope = Scope.getInstance()
        self.config_manager = scope.getConfigurationManager()
        self.event_manager = scope.getEventManager()

        self.event_manager.register_event('EXECUTE_TASK',self.execute_task)
        self.event_manager.register_event('EXECUTE_SCRIPT',self.execute_script)
        self.event_manager.register_event('REQUEST_FILE',self.request_file)
        self.event_manager.register_event('MOVE_FILE',self.move_file)

    def execute_task(self,arg):
        #TODO
        self.logger.debug('[ExecutionManager] Executing task...')

    def move_file(self,arg):
        default_file_path=self.config_manager.get('CONNECTION', 'receiveFileParam')
        j = json.loads(arg)
        #msg_id =str(j['id']).lower()
        target_file_path =str(j['filepath']).lower()
        file_name =str(j['filename']).lower()
        self.logger.debug('[ExecutionManager] %s will be moved to %s' % file_name,target_file_path)
        shutil.move(default_file_path+file_name,target_file_path+file_name)

    def execute_script(self,arg):
        j = json.loads(arg)
        #msg_id =str(j['id']).lower()
        file_path =str(j['filepath']).lower()
        time_stamp=str(j['timestamp']).lower()
        self.logger.debug('[ExecutionManager] Making executable file (%s) for execution' % file_path)
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)
        subprocess.call("/bin/sh "+file_path, shell=True)

    #need to move somewhere else
    def request_file(self,arg):
        j = json.loads(arg)
        #msg_id =str(j['id']).lower()
        file_path =str(j['filepath']).lower()
        time_stamp=str(j['timestamp']).lower()
        self.logger.debug('[ExecutionManager] Requested file is '+file_path)
        message_sender=MessageSender(None,file_path)
        message_sender.connect_to_server()

    def get_md5_file(self,fname):
        self.logger.debug('[ExecutionManager] md5 hashing')
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return str(hash_md5.hexdigest())
