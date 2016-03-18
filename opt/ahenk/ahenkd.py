#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.config.ConfigManager import ConfigManager
from base.deamon.BaseDeamon import BaseDaemon
from base.logger.AhenkLogger import Logger
from base.Scope import Scope
from base.messaging.Messaging import Messaging
from base.messaging.Messager import Messager
from base.execution.ExecutionManager import ExecutionManager
from base.registration.Registration import Registration
from base.messaging.MessageResponseQueue import MessageResponseQueue
from base.event.EventManager import EventManager
from base.plugin.PluginManager import PluginManager
from base.task.TaskManager import TaskManager
from base.database.AhenkDbService import AhenkDbService
import threading,time,sys


class AhenkDeamon(BaseDaemon):
    """docstring for AhenkDeamon"""

    def reload(self,msg):
        # reload service here
        pass

    def run(self):
        print ("Ahenk running...")

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
        logger.info("[AhenkDeamon] Log was set")
        globalscope.setLogger(logger)

        eventManager = EventManager()
        globalscope.setEventManager(eventManager)
        logger.info("[AhenkDeamon] Event Manager was set")

        db_service=AhenkDbService()
        db_service.connect()
        db_service.initialize_table()
        globalscope.setDbService(db_service)
        logger.info("[AhenkDeamon] Data Base Service was set")

        messageManager = Messaging()
        globalscope.setMessageManager(messageManager)
        logger.info("[AhenkDeamon] Message Manager was set")

        pluginManager = PluginManager()
        pluginManager.loadPlugins()
        globalscope.setPluginManager(pluginManager)
        logger.info("[AhenkDeamon] Plugin Manager was set")

        taskManger = TaskManager()
        globalscope.setTaskManager(taskManger)
        logger.info("[AhenkDeamon] Task Manager was set")

        registration=Registration()
        globalscope.setRegistration(registration)
        logger.info("[AhenkDeamon] Registration was set")

        execution_manager=ExecutionManager()
        globalscope.setExecutionManager(execution_manager)
        logger.info("[AhenkDeamon] Execution Manager was set")


        #TODO restrict number of attemption
        while registration.is_registered() is False:
            logger.debug("[AhenkDeamon] Attempting to register")
            registration.registration_request()

        logger.info("[AhenkDeamon] Ahenk is registered")

        messager = Messager()
        messanger_thread = threading.Thread(target=messager.connect_to_server)
        messanger_thread.start()

        while(messager.is_connected() is False):
            time.sleep(1)

        globalscope.setMessager(messager)
        logger.info("[AhenkDeamon] Messager was set")

        if registration.is_ldap_registered() is False:
            logger.debug("[AhenkDeamon] Attempting to registering ldap")
            registration.ldap_registration_request() #TODO work on message

        logger.info("[AhenkDeamon] LDAP registration of Ahenk is completed")


        #login
        logger.info("[AhenkDeamon] Logining...")
        messager.send_direct_message(messageManager.login_msg())

        #request policies
        logger.info("[AhenkDeamon] Requesting policies...")
        messager.send_direct_message(messageManager.policy_request_msg())

        #logout
        #logger.info("[AhenkDeamon] Logouting...")
        #messager.send_direct_message(messageManager.logout_msg())


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
