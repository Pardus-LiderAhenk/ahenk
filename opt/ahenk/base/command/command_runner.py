#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import time
from multiprocessing import Process

from base.agreement.agreement import Agreement
from base.command.command_manager import Commander
from base.scope import Scope
from base.system.system import System
from base.timer.setup_timer import SetupTimer
from base.timer.timer import Timer
from base.util.util import Util


class CommandRunner(object):
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.plugin_manager = scope.get_plugin_manager()
        self.message_manager = scope.get_message_manager()
        self.messenger = scope.get_messenger()
        self.conf_manager = scope.get_configuration_manager()
        self.db_service = scope.get_db_service()
        self.execute_manager = scope.get_execution_manager()

    def check_last_login(self):
        last_login_tmstmp=self.db_service.select_one_result('session', 'timestamp')
        if (int(time.time())-int(last_login_tmstmp))<10:
            return False
        else:
            return True

    def run_command_from_fifo(self, num, stack):
        """ docstring"""

        while True:
            try:
                event = Commander().get_event()
                if event is None:
                    break
                json_data = json.loads(event)
            except Exception as e:
                self.logger.error(
                    'A problem occurred while loading json. Check json format! Error Message: {0}.'
                    ' Event = {1}'.format(str(e), str(event)))
                return

            if json_data is not None:

                self.logger.debug('Signal handled')
                self.logger.debug('Signal is :{0}'.format(str(json_data['event'])))

                if str(json_data['event']) == 'login' and self.check_last_login():
                    username = json_data['username']
                    display = json_data['display']
                    desktop = json_data['desktop']
                    self.logger.info('login event is handled for user: {0}'.format(username))
                    login_message = self.message_manager.login_msg(username)
                    self.messenger.send_direct_message(login_message)

                    agreement = Agreement()
                    agreement_choice = None

                    if agreement.check_agreement(username) is not True:
                        self.logger.debug('User {0} has not accepted agreement.'.format(username))
                        thread_ask = Process(target=agreement.ask, args=(username, display,))
                        thread_ask.start()

                        agreement_timeout = self.conf_manager.get('SESSION', 'agreement_timeout')

                        timeout = int(agreement_timeout)  # sec
                        timer = time.time()
                        while 1:
                            if thread_ask.is_alive() is False:
                                self.logger.warning('{0} was answered the question '.format(username))
                                if Agreement().check_agreement(username) is True:
                                    self.logger.warning('Choice of {0} is YES'.format(username))
                                    agreement_choice = True
                                    break
                                elif Agreement().check_agreement(username) is False:
                                    self.logger.warning('Choice of {0} is NO'.format(username))
                                    agreement_choice = False
                                    Util.close_session(username)
                                    break

                            if (time.time() - timer) > timeout:
                                if thread_ask.is_alive():
                                    thread_ask.terminate()
                                Util.close_session(username)
                                self.logger.warning(
                                    'Session of {0} was ended because of timeout of contract agreement'.format(
                                        username))
                                break
                            time.sleep(1)

                        if agreement_choice is not None:
                            self.messenger.send_direct_message(
                                self.message_manager.agreement_answer_msg(username, agreement_choice))
                    else:
                        agreement_choice = True

                    if agreement_choice is True:
                        self.db_service.delete('session', 'username=\'{0}\''.format(username))

                        self.logger.info(
                            'Display is {0}, desktop env is {1} for {2}'.format(display, desktop,
                                                                                username))
                        session_columns = self.db_service.get_cols('session')
                        self.db_service.update('session', session_columns,
                                               [username, display, desktop, str(int(time.time()))])
                        get_policy_message = self.message_manager.policy_request_msg(username)

                        self.plugin_manager.process_mode('safe', username)
                        self.plugin_manager.process_mode('login', username)

                        kward = dict()
                        kward['timeout_args'] = username
                        kward['checker_args'] = username

                        SetupTimer.start(Timer(timeout=System.Ahenk.get_policy_timeout(),
                                               timeout_function=self.execute_manager.execute_default_policy,
                                               checker_func=self.execute_manager.is_policy_executed, kwargs=kward))

                        self.logger.info(
                            'Requesting updated policies from Lider. If Ahenk could not reach updated '
                            'policies in {0} sec, booked policies will be executed'.format(
                                System.Ahenk.get_policy_timeout()))
                        self.messenger.send_direct_message(get_policy_message)

                elif str(json_data['event']) == 'logout':
                    username = json_data['username']
                    self.db_service.delete('session', 'username=\'{0}\''.format(username))
                    self.execute_manager.remove_user_executed_policy_dict(username)
                    # TODO delete all user records while initializing
                    self.logger.info('logout event is handled for user: {0}'.format(username))
                    logout_message = self.message_manager.logout_msg(username)
                    self.messenger.send_direct_message(logout_message)

                    self.plugin_manager.process_mode('logout', username)
                    self.plugin_manager.process_mode('safe', username)

                elif str(json_data['event']) == 'send':
                    self.logger.info('Sending message over ahenkd command. Response Message: {0}'.format(
                        json.dumps(json_data['message'])))
                    message = json.dumps(json_data['message'])
                    self.messenger.send_direct_message(message)

                elif str(json_data['event']) == 'load':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('All plugins are loading to ahenk')
                        self.plugin_manager.load_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('{0} plugin is loading to ahenk'.format(p_name))
                            self.plugin_manager.load_single_plugin(p_name)

                elif str(json_data['event']) == 'reload':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('All plugins are reloading to ahenk')
                        self.plugin_manager.reload_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('{0} plugin is reloading to ahenk'.format(p_name))
                            self.plugin_manager.reload_single_plugin(p_name)

                elif str(json_data['event']) == 'remove':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('All plugins are removing from ahenk')
                        self.plugin_manager.remove_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('{0} plugin is removing from ahenk'.format(p_name))
                            self.plugin_manager.remove_single_plugin(p_name)

                elif str(json_data['event']) == 'stop':
                    self.plugin_manager.process_mode('shutdown')
                    self.logger.info('Shutdown mode activated.')

                    # TODO timeout
                    while self.running_plugin() is False:
                        self.logger.debug('Waiting for progress of plugins...')
                        time.sleep(0.5)

                    Util.delete_file(System.Ahenk.fifo_file())
                    Scope().get_instance().get_custom_param('ahenk_daemon').stop()
                else:
                    self.logger.error('Unknown command error. Command:' + json_data['event'])
                self.logger.debug('Processing of handled event is completed')

    def running_plugin(self):
        """ docstring"""
        for plugin in self.plugin_manager.plugins:
            if plugin.keep_run is True:
                return False
        return True