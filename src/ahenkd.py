#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import os
import queue
import signal
import sys
import threading
import time
from glob import glob

from base.agreement.agreement import Agreement
from base.command.command_manager import Commander
from base.command.command_runner import CommandRunner
from base.config.config_manager import ConfigManager
from base.database.ahenk_db_service import AhenkDbService
from base.deamon.base_daemon import BaseDaemon
from base.event.event_manager import EventManager
from base.execution.execution_manager import ExecutionManager
from base.logger.ahenk_logger import Logger
from base.messaging.message_response_queue import MessageResponseQueue
from base.messaging.messaging import Messaging
from base.messaging.messenger import Messenger
from base.plugin.plugin_manager_factory import PluginManagerFactory
from base.registration.registration import Registration
from base.scheduler.scheduler_factory import SchedulerFactory
from base.scope import Scope
from base.system.system import System
from base.task.task_manager import TaskManager
from base.util.util import Util
from easygui import msgbox

sys.path.append('../..')

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
        logger.info('Log was set')
        Scope.get_instance().set_logger(logger)
        return logger

    @staticmethod
    def init_config_manager(config_file_path, configfile_folder_path):
        """ docstring"""
        config_manager = ConfigManager(config_file_path, configfile_folder_path)
        config = config_manager.read()
        Scope.get_instance().set_configuration_manager(config)
        return config

    @staticmethod
    def init_scheduler():
        """ docstring"""
        scheduler_ins = SchedulerFactory.get_intstance()
        scheduler_ins.initialize()
        Scope.get_instance().set_scheduler(scheduler_ins)
        sc_thread = threading.Thread(target=scheduler_ins.run)
        sc_thread.setDaemon(True)
        sc_thread.start()
        return scheduler_ins

    @staticmethod
    def init_event_manager():
        """ docstring"""
        event_manager = EventManager()
        Scope.get_instance().set_event_manager(event_manager)
        return event_manager

    @staticmethod
    def init_ahenk_db():
        """ docstring"""
        db_service = AhenkDbService()
        db_service.connect()
        db_service.initialize_table()
        Scope.get_instance().set_sb_service(db_service)
        return db_service

    @staticmethod
    def init_messaging():
        """ docstring"""
        message_manager = Messaging()
        Scope.get_instance().set_message_manager(message_manager)
        return message_manager

    @staticmethod
    def init_plugin_manager():
        """ docstring"""
        plugin_manager = PluginManagerFactory.get_instance()
        Scope.get_instance().set_plugin_manager(plugin_manager)
        # order changed, problem?
        plugin_manager.load_plugins()
        return plugin_manager

    @staticmethod
    def init_task_manager():
        """ docstring"""
        task_manager = TaskManager()
        Scope.get_instance().set_task_manager(task_manager)
        return task_manager

    @staticmethod
    def init_registration():
        """ docstring"""
        registration = Registration()
        Scope.get_instance().set_registration(registration)
        return registration

    @staticmethod
    def init_execution_manager():
        """ docstring"""
        execution_manager = ExecutionManager()
        Scope.get_instance().set_execution_manager(execution_manager)
        return execution_manager

    @staticmethod
    def init_messenger():
        """ docstring"""
        messenger_ = Messenger()
        messenger_.connect_to_server()
        Scope.get_instance().set_messenger(messenger_)
        return messenger_

    @staticmethod
    def init_message_response_queue():
        """ docstring"""
        response_queue = queue.Queue()
        message_response_queue = MessageResponseQueue(response_queue)
        message_response_queue.setDaemon(True)
        message_response_queue.start()
        Scope.get_instance().set_response_queue(response_queue)
        return response_queue

    def check_registration(self):
        """ docstring"""
        # max_attempt_number = int(System.Hardware.Network.interface_size()) * 3
        max_attempt_number = 1
        # self.logger.debug()
        # logger = Scope.getInstance().getLogger()
        registration = Scope.get_instance().get_registration()

        try:
            #if registration.is_registered() is False:
            #    self.logger.debug('Ahenk is not registered. Attempting for registration')
            #    if registration.registration_request() == False:
            #        self.registration_failed()

            if registration.is_registered() is False:
                print("Registation attemp")
                max_attempt_number -= 1
                self.logger.debug('Ahenk is not registered. Attempting for registration')
                registration.registration_request(self.register_hostname,self.register_user_name,self.register_user_password)

                #if max_attempt_number < 0:
                #    self.logger.warning('Number of Attempting for registration is over')
                #    self.registration_failed()
                #    break
        except Exception as e:
            self.registration_failed()
            self.logger.error('Registration failed. Error message: {0}'.format(str(e)))


    def is_registered(self):
        try:
            registration = Scope.get_instance().get_registration()
            if registration.is_registered() is False:
                self.registration_failed()

        except Exception as e:
            self.registration_failed()
            self.logger.error('Registration failed. Error message: {0}'.format(str(e)))

    @staticmethod
    def shutdown_mode():
        """ docstring"""
        scope = Scope().get_instance()
        plugin_manager = scope.get_plugin_manager()
        plugin_manager.process_mode('shutdown')

    def registration_failed(self):
        """ docstring"""
        self.logger.error('Registration failed. All registration attempts were failed. Ahenk is stopping...')
        print('Registration failed. Ahenk is stopping..')
        ahenk_daemon.stop()

    @staticmethod
    def reload_plugins():
        """ docstring"""
        Scope.get_instance().get_plugin_manager().reloadPlugins()

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
            signal.signal(signal.SIGALRM, CommandRunner().run_command_from_fifo)
            self.logger.info('Signal handler is set up')
        except Exception as e:
            self.logger.error('Signal handler could not set up. Error Message: {0} '.format(str(e)))

    @staticmethod
    def init_pid_file():
        """ docstring"""
        with open(System.Ahenk.pid_path(), 'w+') as f:
            f.write(str(os.getpid()))

    @staticmethod
    def init_fifo_file():
        """ docstring"""
        if Util.is_exist(System.Ahenk.fifo_file()):
            Util.delete_file(System.Ahenk.fifo_file())
        Util.create_file(System.Ahenk.fifo_file())
        Util.set_permission(System.Ahenk.fifo_file(), '600')

    def set_register_user(self, hostName, username, password):
        self.register_hostname=hostName
        self.register_user_name=username
        self.register_user_password=password

    def disable_local_users(self):

        self.logger.info('Local users disable action start..')
        conf_manager = Scope.get_instance().get_configuration_manager()

        if conf_manager.has_section('MACHINE'):
            user_disabled = conf_manager.get("MACHINE", "user_disabled")
            self.logger.info('User disabled value=' + str(user_disabled))
            if user_disabled == '0':
                self.logger.info('local user disabling')
                Scope.get_instance().get_registration().disable_local_users()

                conf_manager.set('MACHINE', 'user_disabled', '1')

                with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                    self.logger.info('oepning config file ')
                    conf_manager.write(configfile)

                user_disabled = conf_manager.get("MACHINE", "user_disabled")
                self.logger.info('User succesfully disabled value=' + str(user_disabled))
            else:
                self.logger.info('users already disabled')

    def run(self):
        """ docstring"""
        print('Ahenk running...')

        global_scope = Scope()
        global_scope.set_instance(global_scope)

        config_file_folder_path = '/etc/ahenk/config.d/'

        # configuration manager must be first load
        self.init_config_manager(System.Ahenk.config_path(), config_file_folder_path)

        # Logger must be second
        self.logger = self.init_logger()

        self.init_pid_file()
        self.logger.info('Pid file was created')

        self.init_fifo_file()
        self.logger.info('Fifo file was created')

        self.init_event_manager()
        self.logger.info('Event Manager was set')

        self.init_ahenk_db()
        self.logger.info('DataBase Service was set')

        self.init_messaging()
        self.logger.info('Message Manager was set')

        self.init_plugin_manager()
        self.logger.info('Plugin Manager was set')

        self.init_scheduler()
        self.logger.info('Scheduler was set')

        self.init_task_manager()
        self.logger.info('Task Manager was set')

        self.init_registration()
        self.logger.info('Registration was set')

        self.init_execution_manager()
        self.logger.info('Execution Manager was set')

        self.check_registration()

        self.is_registered()

        self.disable_local_users()

        #self.logger.info('Ahenk was registered')

        self.messenger = self.init_messenger()
        self.logger.info('Messenger was set')

        self.init_signal_listener()
        self.logger.info('Signals listeners was set')

        # Agreement().agreement_contract_update()

        global_scope.put_custom_map('ahenk_daemon', ahenk_daemon)
        self.init_message_response_queue()

        # if registration.is_ldap_registered() is False:
        #    logger.debug('Attempting to registering ldap')
        #    registration.ldap_registration_request() #TODO work on message

        self.logger.info('LDAP registration of Ahenk is completed')

        self.messenger.send_direct_message('test')

        while True:
            time.sleep(1)


if __name__ == '__main__':

    ahenk_daemon = AhenkDaemon(System.Ahenk.pid_path())
    try:
        if len(sys.argv) == 2 and (sys.argv[1] in ('start', 'stop', 'restart', 'status')):
            ahenk_daemon.set_register_user(None, None, None)
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
        elif len(sys.argv) > 2 and (sys.argv[1] in ('register')):
            params = sys.argv[1]
            hostName = sys.argv[2]
            userName = sys.argv[3]
            password = sys.argv[4]
            ahenk_daemon.set_register_user(hostName,userName,password)
            ahenk_daemon.run()

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
