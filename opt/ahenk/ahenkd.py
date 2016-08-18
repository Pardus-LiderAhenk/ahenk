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

ahenk_daemon = None


class AhenkDaemon(BaseDaemon):
    """Ahenk service base class which initializes services and maintains events/commands"""

    @staticmethod
    def reload():
        """ docstring"""
        # reload service here
        pass

    @staticmethod
    def init_logger():
        """ docstring"""
        logger = Logger()
        logger.info('[AhenkDaemon] Log was set')
        Scope.getInstance().setLogger(logger)
        return logger

    @staticmethod
    def init_config_manager(config_file_path, configfile_folder_path):
        """ docstring"""
        config_manager = ConfigManager(config_file_path, configfile_folder_path)
        config = config_manager.read()
        Scope.getInstance().setConfigurationManager(config)
        return config

    @staticmethod
    def init_scheduler():
        """ docstring"""
        scheduler_ins = SchedulerFactory.get_intstance()
        scheduler_ins.initialize()
        Scope.getInstance().set_scheduler(scheduler_ins)
        sc_thread = threading.Thread(target=scheduler_ins.run)
        sc_thread.setDaemon(True)
        sc_thread.start()
        return scheduler_ins

    @staticmethod
    def init_event_manager():
        """ docstring"""
        event_manager = EventManager()
        Scope.getInstance().setEventManager(event_manager)
        return event_manager

    @staticmethod
    def init_ahenk_db():
        """ docstring"""
        db_service = AhenkDbService()
        db_service.connect()
        db_service.initialize_table()
        Scope.getInstance().setDbService(db_service)
        return db_service

    @staticmethod
    def init_messaging():
        """ docstring"""
        message_manager = Messaging()
        Scope.getInstance().setMessageManager(message_manager)
        return message_manager

    @staticmethod
    def init_plugin_manager():
        """ docstring"""
        plugin_manager = PluginManagerFactory.get_instance()
        Scope.getInstance().setPluginManager(plugin_manager)
        # order changed, problem?
        plugin_manager.load_plugins()
        return plugin_manager

    @staticmethod
    def init_task_manager():
        """ docstring"""
        task_manager = TaskManager()
        Scope.getInstance().setTaskManager(task_manager)
        return task_manager

    @staticmethod
    def init_registration():
        """ docstring"""
        registration = Registration()
        Scope.getInstance().setRegistration(registration)
        return registration

    @staticmethod
    def init_execution_manager():
        """ docstring"""
        execution_manager = ExecutionManager()
        Scope.getInstance().setExecutionManager(execution_manager)
        return execution_manager

    @staticmethod
    def init_messenger():
        """ docstring"""
        messenger_ = Messenger()
        messenger_.connect_to_server()
        Scope.getInstance().setMessenger(messenger_)
        return messenger_

    @staticmethod
    def init_message_response_queue():
        """ docstring"""
        response_queue = queue.Queue()
        message_response_queue = MessageResponseQueue(response_queue)
        message_response_queue.setDaemon(True)
        message_response_queue.start()
        Scope.getInstance().setResponseQueue(response_queue)
        return response_queue

    def check_registration(self):
        """ docstring"""
        max_attempt_number = int(System.Hardware.Network.interface_size()) * 3
        # self.logger.debug()
        # logger = Scope.getInstance().getLogger()
        registration = Scope.getInstance().getRegistration()

        try:
            while registration.is_registered() is False:
                max_attempt_number -= 1
                self.logger.debug('[AhenkDaemon] Ahenk is not registered. Attempting for registration')
                registration.registration_request()
                if max_attempt_number < 0:
                    self.logger.warning('[AhenkDaemon] Number of Attempting for registration is over')
                    self.registration_failed()
                    break
        except Exception as e:
            self.logger.error('[AhenkDaemon] Registration failed. Error message: {0}'.format(str(e)))

    @staticmethod
    def shutdown_mode():
        """ docstring"""
        scope = Scope().getInstance()
        plugin_manager = scope.getPluginManager()
        plugin_manager.process_mode('shutdown')

    def registration_failed(self):
        """ docstring"""
        self.logger.error(
            '[AhenkDaemon] Registration failed. All registration attempts were failed. Ahenk is stopping...')
        print('Registration failed. Ahenk is stopping..')
        ahenk_daemon.stop()

    @staticmethod
    def reload_plugins():
        """ docstring"""
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
        """ docstring"""
        # TODO destroy plugin manager here
        self.init_plugin_manager()

    def init_signal_listener(self):
        """ docstring"""
        try:
            signal.signal(signal.SIGALRM, self.run_command_from_fifo)
            self.logger.info('[AhenkDaemon] Signal handler is set up')
        except Exception as e:
            self.logger.error('[AhenkDaemon] Signal handler could not set up. Error Message: {0} '.format(str(e)))

    @staticmethod
    def init_pid_file():
        """ docstring"""
        with open(System.Ahenk.pid_path(), 'w+') as f:
            f.write(str(os.getpid()))

    def run(self):
        """ docstring"""
        print('Ahenk running...')

        global_scope = Scope()
        global_scope.setInstance(global_scope)

        config_file_folder_path = '/etc/ahenk/config.d/'

        # configuration manager must be first load
        self.init_config_manager(System.Ahenk.config_path(), config_file_folder_path)

        # Logger must be second
        self.logger = self.init_logger()

        self.init_pid_file()
        self.logger.info('[AhenkDaemon] Pid file was created')

        self.init_event_manager()
        self.logger.info('[AhenkDaemon] Event Manager was set')

        self.init_ahenk_db()
        self.logger.info('[AhenkDaemon] DataBase Service was set')

        self.init_messaging()
        self.logger.info('[AhenkDaemon] Message Manager was set')

        self.init_plugin_manager()
        self.logger.info('[AhenkDaemon] Plugin Manager was set')

        self.init_scheduler()
        self.logger.info('[AhenkDaemon] Scheduler was set')

        self.init_task_manager()
        self.logger.info('[AhenkDaemon] Task Manager was set')

        self.init_registration()
        self.logger.info('[AhenkDaemon] Registration was set')

        self.init_execution_manager()
        self.logger.info('[AhenkDaemon] Execution Manager was set')

        self.check_registration()
        self.logger.info('[AhenkDaemon] Ahenk was registered')

        self.messenger = self.init_messenger()
        self.logger.info('[AhenkDaemon] Messenger was set')

        self.init_signal_listener()
        self.logger.info('[AhenkDaemon] Signals listeners was set')

        Agreement().agreement_contract_update()

        self.init_message_response_queue()

        # if registration.is_ldap_registered() is False:
        #    logger.debug('[AhenkDaemon] Attempting to registering ldap')
        #    registration.ldap_registration_request() #TODO work on message

        self.logger.info('[AhenkDaemon] LDAP registration of Ahenk is completed')

        self.messenger.send_direct_message('test')



        while True:
            time.sleep(1)

    @staticmethod
    def running_plugin():
        """ docstring"""
        scope = Scope().getInstance()
        plugin_manager = scope.getPluginManager()

        for plugin in plugin_manager.plugins:
            if plugin.keep_run is True:
                return False
        return True

    def run_command_from_fifo(self, num, stack):
        """ docstring"""
        scope = Scope().getInstance()
        plugin_manager = scope.getPluginManager()
        message_manager = scope.getMessageManager()
        messenger = scope.getMessenger()
        conf_manager = scope.getConfigurationManager()
        db_service = scope.getDbService()
        execute_manager = scope.getExecutionManager()

        while True:
            try:
                event = Commander().get_event()
                if event is None:
                    break
                json_data = json.loads(event)
            except Exception as e:
                self.logger.error(
                    '[AhenkDaemon] A problem occurred while loading json. Check json format! Error Message: {0}.'
                    ' Event = {1}'.format(str(e), str(event)))
                return

            if json_data is not None:

                self.logger.debug('[AhenkDaemon] Signal handled')
                self.logger.debug('[AhenkDaemon] Signal is :{0}'.format(str(json_data['event'])))

                if str(json_data['event']) == 'login':
                    username = json_data['username']
                    display = json_data['display']
                    desktop = json_data['desktop']
                    self.logger.info('[AhenkDaemon] login event is handled for user: {0}'.format(username))
                    login_message = message_manager.login_msg(username)
                    messenger.send_direct_message(login_message)

                    agreement = Agreement()
                    agreement_choice = None

                    if agreement.check_agreement(username) is not True:
                        self.logger.debug('[AhenkDaemon] User {0} has not accepted agreement.'.format(username))
                        thread_ask = Process(target=agreement.ask, args=(username, display,))
                        thread_ask.start()

                        agreement_timeout = conf_manager.get('SESSION', 'agreement_timeout')

                        timeout = int(agreement_timeout)  # sec
                        timer = time.time()
                        while 1:
                            if thread_ask.is_alive() is False:
                                self.logger.warning('[AhenkDaemon] {0} was answered the question '.format(username))
                                if Agreement().check_agreement(username) is True:
                                    self.logger.warning('[AhenkDaemon] Choice of {0} is YES'.format(username))
                                    agreement_choice = True
                                    break
                                elif Agreement().check_agreement(username) is False:
                                    self.logger.warning('[AhenkDaemon] Choice of {0} is NO'.format(username))
                                    agreement_choice = False
                                    Util.close_session(username)
                                    break

                            if (time.time() - timer) > timeout:
                                if thread_ask.is_alive():
                                    thread_ask.terminate()
                                Util.close_session(username)
                                self.logger.warning(
                                    '[AhenkDaemon] Session of {0} was ended because of timeout of contract agreement'.format(
                                        username))
                                break
                            time.sleep(1)

                        if agreement_choice is not None:
                            messenger.send_direct_message(message_manager.agreement_answer_msg(username, agreement_choice))
                    else:
                        agreement_choice = True

                    if agreement_choice is True:
                        db_service.delete('session', 'username=\'{0}\''.format(username))

                        self.logger.info(
                            '[AhenkDaemon] Display is {0}, desktop env is {1} for {2}'.format(display, desktop, username))

                        db_service.update('session', scope.getDbService().get_cols('session'),
                                          [username, display, desktop, Util.timestamp()])
                        get_policy_message = message_manager.policy_request_msg(username)

                        plugin_manager.process_mode('safe', username)
                        plugin_manager.process_mode('login', username)

                        kward = dict()
                        kward['timeout_args'] = username
                        kward['checker_args'] = username

                        SetupTimer.start(Timer(timeout=System.Ahenk.get_policy_timeout(),
                                               timeout_function=execute_manager.execute_default_policy,
                                               checker_func=execute_manager.is_policy_executed, kwargs=kward))

                        self.logger.info(
                            '[AhenkDaemon] Requesting updated policies from Lider. If Ahenk could not reach updated '
                            'policies in {0} sec, booked policies will be executed'.format(
                                System.Ahenk.get_policy_timeout()))
                        messenger.send_direct_message(get_policy_message)

                elif str(json_data['event']) == 'logout':
                    username = json_data['username']
                    db_service.delete('session', 'username=\'{0}\''.format(username))
                    execute_manager.remove_user_executed_policy_dict(username)
                    # TODO delete all user records while initializing
                    self.logger.info('[AhenkDaemon] logout event is handled for user: {0}'.format(username))
                    logout_message = message_manager.logout_msg(username)
                    messenger.send_direct_message(logout_message)

                    plugin_manager.process_mode('logout', username)
                    plugin_manager.process_mode('safe', username)

                elif str(json_data['event']) == 'send':
                    self.logger.info('[AhenkDaemon] Sending message over ahenkd command. Response Message: {0}'.format(
                        json.dumps(json_data['message'])))
                    message = json.dumps(json_data['message'])
                    messenger.send_direct_message(message)

                elif str(json_data['event']) == 'load':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('[AhenkDaemon] All plugins are loading to ahenk')
                        plugin_manager.load_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('[AhenkDaemon] {0} plugin is loading to ahenk'.format(p_name))
                            plugin_manager.load_single_plugin(p_name)

                elif str(json_data['event']) == 'reload':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('[AhenkDaemon] All plugins are reloading to ahenk')
                        plugin_manager.reload_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('[AhenkDaemon] {0} plugin is reloading to ahenk'.format(p_name))
                            plugin_manager.reload_single_plugin(p_name)

                elif str(json_data['event']) == 'remove':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('[AhenkDaemon] All plugins are removing from ahenk')
                        plugin_manager.remove_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('[AhenkDaemon] {0} plugin is removing from ahenk'.format(p_name))
                            plugin_manager.remove_single_plugin(p_name)

                elif str(json_data['event']) == 'stop':
                    self.shutdown_mode()
                    self.logger.info('[AhenkDaemon] Shutdown mode activated.')

                    # TODO timeout
                    while self.running_plugin() is False:
                        self.logger.debug('[AhenkDaemon] Waiting for progress of plugins...')
                        time.sleep(0.5)

                    if Util.is_exist('/tmp/liderahenk.fifo'):
                        Util.delete_file('/tmp/liderahenk.fifo')
                    ahenk_daemon.stop()
                else:
                    self.logger.error('[AhenkDaemon] Unknown command error. Command:' + json_data['event'])
                self.logger.debug('[AhenkDaemon] Processing of handled event is completed')
                # return True
            # else:
                # return False


if __name__ == '__main__':

    ahenk_daemon = AhenkDaemon(System.Ahenk.pid_path())
    try:
        if len(sys.argv) == 2 and (sys.argv[1] in ('start', 'stop', 'restart', 'status')):
            if sys.argv[1] == 'start':
                if System.Ahenk.is_running() is True:
                    print('There is already running Ahenk service. It will be killed.[{0}]'.format(
                        str(System.Ahenk.get_pid_number())))
                    System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
                else:
                    print('Ahenk starting...')
                ahenk_daemon.run()
            elif sys.argv[1] == 'stop':
                if System.Ahenk.is_running() is True:
                    raise SystemExit
                else:
                    print('Ahenk not working!')
            elif sys.argv[1] == 'restart':
                if System.Ahenk.is_running() is True:
                    print('Ahenk restarting...')
                    ahenk_daemon.restart()
                else:
                    print('Ahenk starting...')
                    ahenk_daemon.run()
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
                ahenk_daemon.stop()
