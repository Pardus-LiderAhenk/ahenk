#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import subprocess
from base.Scope import Scope
from base.model.Task import Task
from base.model.Policy import Policy
import hashlib,json,os,stat,shutil

class ExecutionManager(object):
    """docstring for FileTransferManager"""

    def __init__(self):
        super(ExecutionManager, self).__init__()

        scope = Scope.getInstance()
        self.config_manager = scope.getConfigurationManager()
        self.event_manager = scope.getEventManager()
        self.task_manager = scope.getTaskManager()
        self.messager = scope.getMessager()
        self.logger=scope.getLogger()
        self.db_service=scope.getDbService()

        self.event_manager.register_event('EXECUTE_SCRIPT',self.execute_script)
        self.event_manager.register_event('REQUEST_FILE',self.request_file)
        self.event_manager.register_event('MOVE_FILE',self.move_file)
        self.event_manager.register_event('EXECUTE_TASK',self.execute_task)
        self.event_manager.register_event('POLICY',self.update_policies)

    def update_policies(self,arg):
        print("updating policies...")

        policy = Policy(json.loads(arg))
        #TODO get username from pam
        username='volkan'

        ahenk_policy_ver=self.db_service.select('policy',['version'],'type = \'A\'')
        user_policy_version=self.db_service.select('policy',['version'],'type = \'U\' and name = \''+username+'\'')
        installed_plugins=self.get_installed_plugins()
        missing_plugins=[]


        if policy.ahenk_policy_version != ahenk_policy_ver[0][0]:
            ahenk_policy_id=self.db_service.select('policy',['id'],'type = \'A\'')
            self.db_service.delete('profile','id='+str(ahenk_policy_id[0][0]))
            self.db_service.update('policy',['version'],[str(policy.ahenk_policy_version)],'type=\'A\'')

            for profile in policy.ahenk_profiles:
                profile_columns=['id','create_date','modify_date','label','description','overridable','active','deleted','profile_data','plugin']
                args=[str(ahenk_policy_id[0][0]),str(profile.create_date),str(profile.modify_date),str(profile.label),
                      str(profile.description),str(profile.overridable),str(profile.active),str(profile.deleted),str(profile.profile_data),str(profile.plugin)]
                self.db_service.update('profile',profile_columns,args)
                if profile.plugin.name not in installed_plugins and profile.plugin.name not in missing_plugins:
                    missing_plugins.append(profile.plugin.name)

        else:
            print("already there ahenk policy")

        if policy.user_policy_version != user_policy_version[0][0]:
            user_policy_id=self.db_service.select('policy',['id'],'type = \'U\' and name=\''+username+'\'')
            self.db_service.delete('profile','id='+str(user_policy_id[0][0]))
            self.db_service.update('policy',['version'],[str(policy.user_policy_version)],'type=\'U\' and name=\''+username+'\'')
            for profile in policy.user_profiles:
                profile_columns=['id','create_date','modify_date','label','description','overridable','active','deleted','profile_data','plugin']
                args = [str(user_policy_id[0][0]),str(profile.create_date),str(profile.modify_date),str(profile.label),
                      str(profile.description),str(profile.overridable),str(profile.active),str(profile.deleted),str(profile.profile_data),str(profile.plugin)]
                self.db_service.update('profile',profile_columns,args)
                if profile.plugin.name not in installed_plugins and profile.plugin.name not in missing_plugins:
                    missing_plugins.append(profile.plugin.name)
        else:
            print("already there user policy")

        print("updated policies")
        print("but first need these plugins:"+str(missing_plugins))

    def get_installed_plugins(self):
        plugins=self.db_service.select('plugin',['name','version'])
        p_list=[]
        for p in plugins:
            p_list.append(str(p[0])+'-'+str(p[1]))
        return p_list

    def execute_task(self,arg):
        self.logger.debug('[ExecutionManager] Adding new  task...')
        task = Task(arg)
        self.task_manager.addTask(task)

    def move_file(self,arg):
        default_file_path=self.config_manager.get('CONNECTION', 'receiveFileParam')
        j = json.loads(arg)
        #msg_id =str(j['id']).lower()
        target_file_path =str(j['filepath']).lower()
        file_name =str(j['filename']).lower()
        self.logger.debug('[ExecutionManager] '+file_name+' will be moved to '+target_file_path)
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
        self.messager.send_file(file_path)

    def get_md5_file(self,fname):
        self.logger.debug('[ExecutionManager] md5 hashing')
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return str(hash_md5.hexdigest())
