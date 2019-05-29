#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>


import configparser
import datetime
import json
import os
import queue as Queue
import threading

from base.command.fifo import Fifo
from base.model.enum.content_type import ContentType
from base.model.enum.message_code import MessageCode
from base.model.enum.message_type import MessageType
from base.system.system import System
from base.util.util import Util


class Commander(object):
    def __init__(self):
        pass

    def set_event(self, *args):

        if args is None or len(args) < 1:
            print('Lack of arguments')

        params = args[0]
        data = dict()

        if System.Ahenk.is_running() is True:

            if len(params) > 1 and params[1] == 'clean':
                print('Ahenk stopping')
                System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
                self.clean()
                return False

            elif len(params) > 4 and params[1] == 'login':
                print('{0} logging in'.format(str(params[2])))
                data['event'] = params[1]
                data['username'] = params[2]
                data['desktop'] = params[3]
                data['display'] = params[4]
                if len(params) == 6:
                    data['ip'] = params[5]

            elif len(params) == 3 and params[1] == 'logout':
                print('{0} logging out'.format(str(params[2])))
                data['event'] = params[1]
                data['username'] = params[2]
                
            elif len(params) == 4 and params[1] == 'logout':
                print('{0} logging out'.format(str(params[2])))
                data['event'] = params[1]
                data['username'] = params[2]
                data['ip'] = params[3]

            elif len(params) == 2 and params[1] == 'stop':
                data['event'] = 'stop'

            elif len(params) == 4 and params[1] == 'load' and params[2] == '-p':
                data['event'] = 'load'
                data['plugins'] = params[3]

            elif len(params) == 4 and params[1] == 'reload' and params[2] == '-p':
                data['event'] = 'reload'
                data['plugins'] = params[3]

            elif len(params) == 4 and params[1] == 'remove' and params[2] == '-p':
                data['event'] = 'remove'
                data['plugins'] = params[3]

            elif len(params) > 1 and params[1] == 'unregister':
                data['event'] = params[1]


            elif len(params) > 5 and params[1] == 'send':
                data['event'] = params[1]
                response = dict()
                response['timestamp'] = str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))
                response['responseMessage'] = 'This content was sent via ahenk terminal command'

                if params[2] == '-t':
                    response['responseCode'] = MessageCode.TASK_PROCESSED.value
                    response['type'] = MessageType.TASK_STATUS.value
                    response['taskId'] = params[3]
                    if params[4] == '-m':
                        response['contentType'] = ContentType.APPLICATION_JSON.value
                        response['responseData'] = params[5]
                    elif params[4] == '-f':
                        if os.path.exists(str(params[5])):
                            response['contentType'] = self.get_relevant_type(str(params[5]))
                            response['responseData'] = Util.read_file(str(params[5]), 'rb')
                    else:
                        print(
                            'Wrong or missing parameter. Usage: send -t <task_id> -m|-f <message_content>|<file_path>')
                        return None

                    if len(params) > 6:
                        if params[6] == '-e':
                            response['responseCode'] = MessageCode.TASK_ERROR.value
                        elif params[6] == '-w':
                            response['responseCode'] = MessageCode.TASK_WARNING.value
                        elif params[6] == '-s':
                            response['responseCode'] = MessageCode.TASK_PROCESSED.value
                        else:
                            print(
                                'Wrong or missing parameter.(-e|-s|-w parameters are optional) Usage: send -t <task_id> -m|-f <message_content>|<file_path> -e|-s|-w')
                            return None

                elif len(params) > 7 and params[2] == '-p':
                    response['responseCode'] = MessageCode.POLICY_PROCESSED.value
                    response['type'] = MessageType.POLICY_STATUS.value
                    response['policyVersion'] = params[3]

                    if params[4] == '-c':
                        response['commandExecutionId'] = params[5]

                        if params[6] == '-m':
                            response['contentType'] = ContentType.APPLICATION_JSON.value
                            response['responseData'] = params[7]
                        elif params[6] == '-f':
                            if os.path.exists(str(params[7])):
                                response['contentType'] = self.get_relevant_type(str(params[7]))
                                response['responseData'] = Util.read_file(str(params[7]), 'rb')
                        else:
                            print(
                                'Wrong or missing parameter. Usage: send -p <policy_version> -c <command_execution_id> -m|-f <message_content>|<file_path>')
                            return None

                        if len(params) > 8:
                            if params[8] == '-e':
                                response['responseCode'] = MessageCode.POLICY_ERROR.value
                            elif params[8] == '-w':
                                response['responseCode'] = MessageCode.POLICY_WARNING.value
                            elif params[8] == '-s':
                                response['responseCode'] = MessageCode.POLICY_PROCESSED.value
                            else:
                                print(
                                    'Wrong or missing parameter.(-e|-s|-w parameters are optional) Usage: send -p <policy_version> -c <command_execution_id> -m|-f <message_content>|<file_path> -e|-s|-w')
                                return None
                    else:
                        print(
                            'Wrong or missing parameter. Usage: send -p <policy_version> -c <command_execution_id> -m|-f <message_content>|<file_path> -e|-s|-w')
                        return None

                resp = str(response).replace("\"{", "{")
                resp = resp.replace("}\"", "}")
                resp = resp.replace("'", "\"")
                data['message'] = json.loads(resp)
                # data['message'] = ast.literal_eval(str(response))

            else:
                print('Wrong or missing parameter. Usage : %s start|stop|restart|status|clean|send')
                return None
        else:

            if params[1] == 'clean':
                self.clean()

            else:
                print('Ahenk not running!')
                return None

        if len(data) > 0:
            fifo = Fifo()
            thread = threading.Thread(target=fifo.push(str(json.dumps(data)) + '\n'))
            thread.start()

        return True

    def get_relevant_type(self, extension):

        extension = extension.lower()
        if extension == 'json':
            return ContentType.APPLICATION_JSON
        elif extension == 'txt':
            return ContentType.TEXT_PLAIN
        elif extension == 'dec':
            return ContentType.APPLICATION_MS_WORD
        elif extension == 'pdf':
            return ContentType.APPLICATION_PDF
        elif extension == 'xls':
            return ContentType.APPLICATION_VND_MS_EXCEL
        elif extension == 'jpeg' or extension == 'jpg':
            return ContentType.IMAGE_JPEG
        elif extension == 'png':
            return ContentType.IMAGE_PNG
        elif extension == 'html' or extension == 'htm':
            return ContentType.TEXT_HTML
        else:
            return ContentType.TEXT_PLAIN

    def get_event(self):
        fifo = Fifo()
        queue = Queue.Queue()
        thread = threading.Thread(target=fifo.pull(queue))
        thread.start()
        thread.join()
        result = queue.get()
        if result is not None:
            return result
        else:
            return None

    def clean(self):
        print('Ahenk cleaning..')
        try:
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            db_path = config.get('BASE', 'dbPath')

            if Util.is_exist(System.Ahenk.fifo_file()):
                Util.delete_file(System.Ahenk.fifo_file())

            if Util.is_exist(db_path):
                Util.delete_file(db_path)

            if Util.is_exist(System.Ahenk.pid_path()):
                Util.delete_file(System.Ahenk.pid_path())

            config.set('CONNECTION', 'uid', '')
            config.set('CONNECTION', 'password', '')

            with open(System.Ahenk.config_path(), 'w') as file:
                config.write(file)
            file.close()
            print('Ahenk cleaned.')
        except Exception as e:
            print('Error while running clean command. Error Message {0}'.format(str(e)))

    def status(self):
        ahenk_state = False

        if System.Ahenk.is_running() is True:
            ahenk_state = True
        return "Ahenk Active:{0}\nInstalled Plugins:{1}".format(ahenk_state, str(System.Ahenk.installed_plugins()))

    def force_clean(self):
        # TODO
        pass
