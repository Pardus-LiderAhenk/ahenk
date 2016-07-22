#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import os
import queue
import signal
import sys
import threading
import time
from multiprocessing import Process

from base.Scope import Scope
from base.agreement.agreement import Agreement
from base.command.commander import Commander
from base.config.ConfigManager import ConfigManager
from base.database.AhenkDbService import AhenkDbService
from base.deamon.BaseDeamon import BaseDaemon
from base.event.EventManager import EventManager
from base.execution.ExecutionManager import ExecutionManager
from base.logger.AhenkLogger import Logger
from base.messaging.MessageResponseQueue import MessageResponseQueue
from base.messaging.Messaging import Messaging
from base.messaging.Messenger import Messenger
from base.plugin.plugin_manager_factory import PluginManagerFactory
from base.registration.Registration import Registration
from base.scheduler.scheduler_factory import SchedulerFactory
from base.system.system import System
from base.task.TaskManager import TaskManager
from base.timer.setup_timer import SetupTimer
from base.timer.timer import Timer
from base.util.util import Util

ahenkdaemon = None


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
        return scheduler_ins

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
        pluginManager = PluginManagerFactory.get_instance()
        Scope.getInstance().setPluginManager(pluginManager)
        # order changed, problem?
        pluginManager.load_plugins()
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

    def init_messenger(self):
        messenger = Messenger()
        messenger.connect_to_server()
        Scope.getInstance().setMessenger(messenger)
        return messenger

    def init_message_response_queue(self):
        responseQueue = queue.Queue()
        messageResponseQueue = MessageResponseQueue(responseQueue)
        messageResponseQueue.setDaemon(True)
        messageResponseQueue.start()
        Scope.getInstance().setResponseQueue(responseQueue)
        return responseQueue

    def check_registration(self):
        max_attemp_number = int(System.Hardware.Network.interface_size()) * 3
        logger = Scope.getInstance().getLogger()
        registration = Scope.getInstance().getRegistration()

        try:
            while registration.is_registered() is False:
                # while Scope.getInstance().getRegistration().is_registered() is False:
                max_attemp_number -= 1
                logger.debug('[AhenkDeamon] Ahenk is not registered. Attempting for registration')
                # TODO 'Could not reach Registration response from Lider. Be sure Lider is running and it is connected to XMPP server!'

                registration.registration_request()
                # Scope.getInstance().getRegistration().registration_request()
                if max_attemp_number < 0:
                    logger.warning('[AhenkDeamon] Number of Attempting for registration is over')
                    self.registration_failed()
                    break
        except Exception as e:
            logger.error('[AhenkDeamon] Registration failed. Error message: {}'.format(str(e)))

    def shutdown_mode(self):
        scope = Scope().getInstance()
        plugin_manager = scope.getPluginManager()
        plugin_manager.process_mode('shutdown')

    def registration_failed(self):
        self.logger.error('[AhenkDeamon] Registration failed. All registration attemps were failed. Ahenk is stopping...')
        print('Registration failed. Ahenk is stopping..')
        ahenkdaemon.stop()

    def reload_plugins(self):
        Scope.getInstance().getPluginManager().reloadPlugins()

    def reload_configuration(self):
        # Not implemented yet
        pass

    def reload_messaging(self):
        # Not implemented yet
        pass

    def reload_logger(self):
        # Not implemented yet
        pass

    def update_plugin_manager(self):
        # TODO destroy plugin manager here
        self.init_plugin_manager()

    def init_signal_listener(self):
        try:
            signal.signal(signal.SIGALRM, self.run_command_from_fifo)
            self.logger.info('[AhenkDeamon] Signal handler is set up')
        except Exception as e:
            self.logger.error('[AhenkDeamon] Signal handler could not set up. Error Message: {} '.format(str(e)))

    def init_pid_file(self):
        with open(System.Ahenk.pid_path(), 'w+') as f:
            f.write(str(os.getpid()))

    def run(self):
        print('Ahenk running...')

        globalscope = Scope()
        globalscope.setInstance(globalscope)

        configfileFolderPath = '/etc/ahenk/config.d/'

        # configuration manager must be first load
        self.init_config_manager(System.Ahenk.config_path(), configfileFolderPath)

        # Logger must be second
        self.logger = self.init_logger()

        self.init_pid_file()
        self.logger.info('[AhenkDeamon] Pid file was created')

        self.init_event_manager()
        self.logger.info('[AhenkDeamon] Event Manager was set')

        self.init_ahenk_db()
        self.logger.info('[AhenkDeamon] DataBase Service was set')

        self.init_messaging()
        self.logger.info('[AhenkDeamon] Message Manager was set')

        self.init_plugin_manager()
        self.logger.info('[AhenkDeamon] Plugin Manager was set')

        self.init_scheduler()
        self.logger.info('[AhenkDeamon] Scheduler was set')

        self.init_task_manager()
        self.logger.info('[AhenkDeamon] Task Manager was set')

        self.init_registration()
        self.logger.info('[AhenkDeamon] Registration was set')

        self.init_execution_manager()
        self.logger.info('[AhenkDeamon] Execution Manager was set')

        self.check_registration()
        self.logger.info('[AhenkDeamon] Ahenk was registered')

        self.messenger = self.init_messenger()
        self.logger.info('[AhenkDeamon] Messenger was set')

        self.init_signal_listener()
        self.logger.info('[AhenkDeamon] Signals listeners was set')

        Agreement().agreement_contract_update()

        self.init_message_response_queue()

        # if registration.is_ldap_registered() is False:
        #    logger.debug('[AhenkDeamon] Attempting to registering ldap')
        #    registration.ldap_registration_request() #TODO work on message

        self.logger.info('[AhenkDeamon] LDAP registration of Ahenk is completed')

        self.messenger.send_direct_message('test')

        while True:
            # if messager.is_connected() is False:
            #     self.logger.debug('reconnecting')
            #     Scope.getInstance().getLogger().warning('[AhenkDeamon] Connection is lost. Ahenk is trying for reconnection')
            #     messager = self.init_messager()
            time.sleep(1)

    def running_plugin(self):
        scope = Scope().getInstance()
        plugin_manager = scope.getPluginManager()

        for plugin in plugin_manager.plugins:
            if plugin.keep_run is True:
                return False
        return True

    def run_command_from_fifo(self, num, stack):

        json_data = json.loads(Commander().get_event())

        if json_data is not None:
            scope = Scope().getInstance()
            plugin_manager = scope.getPluginManager()
            message_manager = scope.getMessageManager()
            messenger = scope.getMessenger()
            conf_manager = scope.getConfigurationManager()
            db_service = scope.getDbService()
            execute_manager = scope.getExecutionManager()

            self.logger.debug('[AhenkDeamon] Signal handled')
            self.logger.debug('[AhenkDeamon] Signal is :{}'.format(str(json_data['event'])))

            if 'login' == str(json_data['event']):
                username = json_data['username']
                display = json_data['display']
                desktop = json_data['desktop']
                self.logger.info('[AhenkDeamon] login event is handled for user: {}'.format(username))
                login_message = message_manager.login_msg(username)
                messenger.send_direct_message(login_message)

                agreement = Agreement()
                agreement_choice = None

                if agreement.check_agreement(username) is not True:
                    self.logger.debug('[AhenkDeamon] User {} has not accepted agreement.'.format(username))
                    thread_ask = Process(target=agreement.ask, args=(username, display,))
                    thread_ask.start()

                    agreement_timeout = conf_manager.get('SESSION', 'agreement_timeout')

                    timeout = int(agreement_timeout)  # sec
                    timer = time.time()
                    while 1:
                        if thread_ask.is_alive() is False:
                            self.logger.warning('[AhenkDeamon] {} was answered the question '.format(username))
                            if Agreement().check_agreement(username) is True:
                                self.logger.warning('[AhenkDeamon] Choice of {} is YES'.format(username))
                                agreement_choice = True
                                break
                            elif Agreement().check_agreement(username) is False:
                                self.logger.warning('[AhenkDeamon] Choice of {} is NO'.format(username))
                                agreement_choice = False
                                Util.execute('pkill -9 -u {}'.format(username))
                                break

                        if (time.time() - timer) > timeout:
                            if thread_ask.is_alive():
                                thread_ask.terminate()
                            Util.execute('pkill -9 -u {}'.format(username))
                            self.logger.warning('[AhenkDeamon] Session of {} was ended because of timeout of contract agreement'.format(username))
                            break
                        time.sleep(1)

                    if agreement_choice is not None:
                        messenger.send_direct_message(message_manager.agreement_answer_msg(username, agreement_choice))
                else:
                    agreement_choice = True

                if agreement_choice is True:
                    db_service.delete('session', 'username=\'{0}\''.format(username))

                    self.logger.info('[AhenkDeamon] Display is {0}, desktop env is {1} for {2}'.format(display, desktop, username))

                    db_service.update('session', scope.getDbService().get_cols('session'), [username, display, desktop, Util.timestamp()])
                    get_policy_message = message_manager.policy_request_msg(username)

                    plugin_manager.process_mode('safe', username)
                    plugin_manager.process_mode('login', username)

                    kward = {}
                    kward['timeout_args'] = username
                    kward['checker_args'] = username
                    SetupTimer.start(Timer(timeout=System.Ahenk.get_policy_timeout(), timeout_function=execute_manager.execute_default_policy, checker_func=execute_manager.is_policy_executed, kwargs=kward))

                    self.logger.info('[AhenkDeamon] Requesting updated policies from Lider. If Ahenk could not reach updated policies in {0} sec, booked policies will be executed'.format(System.Ahenk.get_policy_timeout()))
                    messenger.send_direct_message(get_policy_message)

            elif 'logout' == str(json_data['event']):
                username = json_data['username']
                db_service.delete('session', 'username=\'{}\''.format(username))
                execute_manager.remove_user_executed_policy_dict(username)
                # TODO delete all user records while initializing
                self.logger.info('[AhenkDeamon] logout event is handled for user: {}'.format(username))
                logout_message = message_manager.logout_msg(username)
                messenger.send_direct_message(logout_message)

                plugin_manager.process_mode('logout', username)
                plugin_manager.process_mode('safe', username)

            elif 'send' == str(json_data['event']):
                self.logger.info('[AhenkDeamon] Sending message over ahenkd command. Response Message: {}'.format(str(json_data['message'])))
                message = str(json.dumps(json_data['message']))
                messenger.send_direct_message(message)

            elif 'load' == str(json_data['event']):
                plugin_name = str(json_data['plugins'])

                if plugin_name == 'all':
                    self.logger.debug('[AhenkDeamon] All plugins are loading to ahenk')
                    plugin_manager.load_plugins()
                else:
                    for p_name in plugin_name.split(','):
                        self.logger.debug('[AhenkDeamon] {} plugin is loading to ahenk'.format(p_name))
                        plugin_manager.load_single_plugin(p_name)

            elif 'reload' == str(json_data['event']):
                plugin_name = str(json_data['plugins'])

                if plugin_name == 'all':
                    self.logger.debug('[AhenkDeamon] All plugins are reloading to ahenk')
                    plugin_manager.reload_plugins()
                else:
                    for p_name in plugin_name.split(','):
                        self.logger.debug('[AhenkDeamon] {} plugin is reloading to ahenk'.format(p_name))
                        plugin_manager.reload_single_plugin(p_name)

            elif 'remove' == str(json_data['event']):
                plugin_name = str(json_data['plugins'])

                if plugin_name == 'all':
                    self.logger.debug('[AhenkDeamon] All plugins are removing from ahenk')
                    plugin_manager.remove_plugins()
                else:
                    for p_name in plugin_name.split(','):
                        self.logger.debug('[AhenkDeamon] {} plugin is removing from ahenk'.format(p_name))
                        plugin_manager.remove_single_plugin(p_name)

            elif 'stop' == str(json_data['event']):
                self.shutdown_mode()
                self.logger.info('[AhenkDeamon] Shutdown mode activated.')

                # TODO timeout
                while self.running_plugin() is False:
                    self.logger.debug('[AhenkDeamon] Waiting for progress of plugins...')
                    time.sleep(0.5)
                ahenkdaemon.stop()
            else:
                self.logger.error('[AhenkDeamon] Unknown command error. Command:' + json_data['event'])
            self.logger.debug('[AhenkDeamon] Processing of handled event is completed')
            return True
        else:
            return False


if __name__ == '__main__':

    ahenkdaemon = AhenkDeamon(System.Ahenk.pid_path())
    try:
        if len(sys.argv) == 2 and (sys.argv[1] in ('start', 'stop', 'restart', 'status')):
            if sys.argv[1] == 'start':
                if System.Ahenk.is_running() is True:
                    print('There is already running Ahenk service. It will be killed.[{}]'.format(str(System.Ahenk.get_pid_number())))
                    System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
                else:
                    print('Ahenk starting...')
                ahenkdaemon.run()
            elif sys.argv[1] == 'stop':
                if System.Ahenk.is_running() is True:
                    raise SystemExit
                else:
                    print('Ahenk not working!')
            elif sys.argv[1] == 'restart':
                if System.Ahenk.is_running() is True:
                    print('Ahenk restarting...')
                    ahenkdaemon.restart()
                else:
                    print('Ahenk starting...')
                    ahenkdaemon.run()
            elif sys.argv[1] == 'status':
                print(Commander().status())
            else:
                print('Unknown command. Usage : %s start|stop|restart|status|clean' % sys.argv[0])
                sys.exit(2)
        else:
            result = Commander().set_event(sys.argv)
            if result is None:
                print('Usage : {0} start|stop|restart|status|clean'.format(sys.argv[0]))
                sys.exit(2)
            elif result is True:
                if System.Ahenk.is_running() is True:
                    os.kill(int(System.Ahenk.get_pid_number()), signal.SIGALRM)
    except(KeyboardInterrupt, SystemExit):
        if System.Ahenk.is_running() is True:
            print('Ahenk stopping...')
            result = Commander().set_event([None, 'stop'])
            if result is True:
                if System.Ahenk.is_running() is True:
                    os.kill(int(System.Ahenk.get_pid_number()), signal.SIGALRM)
            else:
                ahenkdaemon.stop()
