#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import configparser
import os
import queue
import signal
import sys
import threading
import time

from base.Scope import Scope
from base.config.ConfigManager import ConfigManager
from base.database.AhenkDbService import AhenkDbService
from base.deamon.BaseDeamon import BaseDaemon
from base.event.EventManager import EventManager
from base.execution.ExecutionManager import ExecutionManager
from base.logger.AhenkLogger import Logger
from base.messaging.MessageResponseQueue import MessageResponseQueue
from base.messaging.Messager import Messager
from base.messaging.Messaging import Messaging
from base.plugin.PluginManager import PluginManager
from base.registration.Registration import Registration
from base.task.TaskManager import TaskManager
from base.scheduler.scheduler_factory import SchedulerFactory

pidfilePath = '/var/run/ahenk.pid'


class AhenkDeamon(BaseDaemon):
    """docstring for AhenkDeamon"""

    def reload(self):
        # reload service here
        pass

    def init_logger(self):
        logger = Logger()
        logger.info('[AhenkDeamon] Log was set')
        Scope.getInstance().setLogger(logger)
        return logger

    def init_config_manager(self, configFilePath, configfileFolderPath):
        configManager = ConfigManager(configFilePath, configfileFolderPath)
        config = configManager.read()
        Scope.getInstance().setConfigurationManager(config)
        return config

    def init_scheduler(self):
        scheduler_ins = SchedulerFactory.get_intstance()
        scheduler_ins.initialize()
        Scope.getInstance().set_scheduler(scheduler_ins)
        sc_thread = threading.Thread(target=scheduler_ins.run)
        sc_thread.setDaemon(True)
        sc_thread.start()

    def init_event_manager(self):
        eventManager = EventManager()
        Scope.getInstance().setEventManager(eventManager)
        return eventManager

    def init_ahenk_db(self):
        db_service = AhenkDbService()
        db_service.connect()
        db_service.initialize_table()
        Scope.getInstance().setDbService(db_service)
        return db_service

    def init_messaging(self):
        messageManager = Messaging()
        Scope.getInstance().setMessageManager(messageManager)
        return messageManager

    def init_plugin_manager(self):
        pluginManager = PluginManager()
        pluginManager.loadPlugins()
        Scope.getInstance().setPluginManager(pluginManager)
        return pluginManager

    def init_task_manager(self):
        taskManager = TaskManager()
        Scope.getInstance().setTaskManager(taskManager)
        return taskManager

    def init_registration(self):
        registration = Registration()
        Scope.getInstance().setRegistration(registration)
        return registration

    def init_execution_manager(self):
        execution_manager = ExecutionManager()
        Scope.getInstance().setExecutionManager(execution_manager)
        return execution_manager

    def init_messager(self):
        messager = Messager()
        messanger_thread = threading.Thread(target=messager.connect_to_server)
        messanger_thread.start()

        while messager.is_connected() is False:
            time.sleep(1)
        time.sleep(5)

        Scope.getInstance().setMessager(messager)
        return messager

    def init_message_response_queue(self):
        responseQueue = queue.Queue()
        messageResponseQueue = MessageResponseQueue(responseQueue)
        messageResponseQueue.setDaemon(True)
        messageResponseQueue.start()
        Scope.getInstance().setResponseQueue(responseQueue)
        return responseQueue

    def check_registration(self):
        # TODO restrict number of attemption
        while Scope.getInstance().getRegistration().is_registered() is False:
            print('registration need')
            Scope.getInstance().getLogger().debug('[AhenkDeamon] Attempting to register')
            Scope.getInstance().getRegistration().registration_request()

    def run(self):
        print('Ahenk running...')

        globalscope = Scope()
        globalscope.setInstance(globalscope)

        configFilePath = '/etc/ahenk/ahenk.conf'
        configfileFolderPath = '/etc/ahenk/config.d/'

        # configuration manager must be first load
        self.init_config_manager(configFilePath, configfileFolderPath)

        # Logger must be second
        logger = self.init_logger()

        self.init_event_manager()
        logger.info('[AhenkDeamon] Event Manager was set')

        self.init_ahenk_db()
        logger.info('[AhenkDeamon] DataBase Service was set')

        self.init_messaging()
        logger.info('[AhenkDeamon] Message Manager was set')

        self.init_plugin_manager()
        logger.info('[AhenkDeamon] Plugin Manager was set')

        self.init_task_manager()
        logger.info('[AhenkDeamon] Task Manager was set')

        #self.init_registration()
        logger.info('[AhenkDeamon] Registration was set')

        self.init_execution_manager()
        logger.info('[AhenkDeamon] Execution Manager was set')

        #self.check_registration()
        logger.info('[AhenkDeamon] Ahenk is registered')

        messager = self.init_messager()
        logger.info('[AhenkDeamon] Messager was set')

        self.init_message_response_queue()


        # if registration.is_ldap_registered() is False:
        #    logger.debug('[AhenkDeamon] Attempting to registering ldap')
        #    registration.ldap_registration_request() #TODO work on message

        logger.info('[AhenkDeamon] LDAP registration of Ahenk is completed')

        # TODO###############
        cnfg = configparser.ConfigParser()
        cnfg.add_section('PID')
        cnfg.set('PID', 'pid_number', str(os.getpid()))

        with open(pidfilePath, 'w') as config_file:
            cnfg.write(config_file)
        # TODO##############

        try:
            signal.signal(signal.SIGALRM, self.signal_handler)
            logger.info('[AhenkDeamon] Signal handler is set up')
        except Exception as e:
            logger.error('[AhenkDeamon] Signal handler could not set up :' + e.errno + '-' + e.strerror)

        messager.send_direct_message('test')

        while True:
            time.sleep(1)

    def signal_handler(self, num, stack):
        print("signal handled")
        # TODO######
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(pidfilePath)
        event = config.get('PID', 'event')
        # TODO######

        params = event.split()
        scope = Scope().getInstance()
        logger = scope.getLogger()

        if 'login' == str(params[0]):
            message = scope.getMessageManager().policy_request_msg(params[1])
            scope.getMessager().send_direct_message(message)
            logger.debug('[AhenkDeamon] login event is handled for user:' + params[1])
        elif 'logout' == str(params[0]):
            message = scope.getMessageManager().logout_msg(params[1])
            scope.getMessager().send_direct_message(message)
            logger.debug('[AhenkDeamon] logout event is handled for user:' + params[1])
        elif 'exit' == str(params[0]):
            print("exit:"+str(params[0]))
            scope = Scope.getInstance()
            scope.getMessager().disconnect()
            #TODO kill thread
            print('stopping ahenk')
        else:
            logger.error('[AhenkDeamon] Unknown command error. Command:' + params[0])

        logger.debug('[AhenkDeamon] Processing of handled event is completed')


def get_pid_number():
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read(pidfilePath)
    return config.get('PID', 'pid_number')


def set_event(event_param):
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read(pidfilePath)
    config.set('PID', 'event', event_param)

    with open(pidfilePath, 'w') as config_file:
        config.write(config_file)


if __name__ == '__main__':

    ahenkdaemon = AhenkDeamon(pidfilePath)
    try:
        if len(sys.argv) == 2:
            if sys.argv[1] == 'start':
                print('starting')
                ahenkdaemon.run()
            elif sys.argv[1] == 'stop':
                ahenkdaemon.stop()
            elif sys.argv[1] == 'restart':
                ahenkdaemon.restart()
            elif sys.argv[1] == 'status':
                print('status')
            else:
                print('Unknown command. Usage : %s start|stop|restart|status' % sys.argv[0])
                sys.exit(2)

        elif len(sys.argv) == 3:
            if sys.argv[1] == 'login' or sys.argv[1] == 'logout':
                print('event:' + str(sys.argv[1]))
                set_event(str(sys.argv[1]) + ' ' + sys.argv[2])
                os.kill(int(get_pid_number()), signal.SIGALRM)
            else:
                print('Unknown command. Usage : %s start|stop|restart|status' % sys.argv[0])
                sys.exit(2)
            sys.exit(0)
        else:
            print('Usage : %s start|stop|restart|status' % sys.argv[0])
            sys.exit(2)
    except(KeyboardInterrupt, SystemExit):
        if str(os.getpid()) == get_pid_number():
            set_event('exit true')
            os.kill(int(get_pid_number()), signal.SIGALRM)
