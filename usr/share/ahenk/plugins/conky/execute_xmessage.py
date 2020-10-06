#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Edip YILDIZ
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

from base.model.enum.content_type import ContentType
import json
from base.plugin.abstract_plugin import AbstractPlugin
import threading


class RunXMessageCommand(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        # self.xmessage_command= "su {0} -c 'export DISPLAY={1} && export XAUTHORITY=~{2}/.Xauthority && xmessage \"{3}\" ' "

        self.custom_message_command = "su {0} -c 'export DISPLAY={1} && export XAUTHORITY=~{2}/.Xauthority && python3 /usr/share/ahenk/plugins/conky/ask.py \"LİDER AHENK BİLDİRİ\" \"{3}\" ' "

        # command for ltsp
        self.custom_message_command_ltsp = "su {0} -c 'export DISPLAY={1} && export XAUTHORITY=~{2}/.Xauthority && python3 /usr/share/ahenk/plugins/conky/ask.py \"LİDER AHENK\\\ BİLDİRİ \" \"{3}\" ' "

    def execute_xmessage(self, message):
        users = self.Sessions.user_name()
        self.logger.debug('[XMessage] users : ' + str(users))
        desktop_env = self.get_desktop_env()
        self.logger.info("Get desktop environment is {0}".format(desktop_env))

        # for user in users:
        user = self.get_username()
        user_display = self.Sessions.display(user)
        user_ip = self.Sessions.userip(user)
        if desktop_env == "gnome":
            user_display = self.get_username_display_gnome(user)
        if user_display is None:
            self.logger.debug('[XMessage] executing for display none for user  ' + str(user))
        else:
            self.logger.debug('[XMessage] user display ' + str(user_display) + ' user ' + str(user))
            if user_ip is None:
                self.execute(self.custom_message_command.format(self.get_as_user(), user_display, self.get_as_user(), message))
                # t = threading.Thread(
                #     target=self.execute(self.custom_message_command.format(self.get_as_user(), user_display, self.get_as_user(), message)))
                # t.start()
            else:
                # message format for ltsp
                self.logger.debug('user_ip: ' + str(user_ip) + ' user_display: ' + str(user_display))
                message_list = []
                message_parser = message.split(" ")
                self.logger.debug('running parser:--->> ' + str(message_parser))
                for msg in message_parser:
                    message = '\\\ ' + str(msg)
                    message_list.append(message)
                    self.logger.debug('message_list:--->> ' + str(message_list))
                message = ''.join(str(x) for x in message_list)
                self.logger.debug('message: ' + str(message))
                t = threading.Thread(
                    target=self.execute(self.custom_message_command_ltsp.format(user, user_display, user, message),
                                        ip=user_ip))
                t.start()

        self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                     message='İşlem başarıyla gerçekleştirildi.',
                                     data=json.dumps({'Result': message}),
                                     content_type=ContentType.APPLICATION_JSON.value)

    def execute_user_message(self, selected_user, message):

        users = self.Sessions.user_name()
        self.logger.debug('[XMessage] users : ' + str(users))

        for user in users:
            if selected_user in user:
                user_display = self.Sessions.display(user)
                user_ip = self.Sessions.userip(user)

                if user_display is None:
                    self.logger.debug('[XMessage] executing for display none for user  ' + str(user))

                else:
                    self.logger.debug('[XMessage] user display ' + str(user_display) + ' user ' + str(user))

                    if user_ip is None:
                        t = threading.Thread(target=self.execute(
                            self.custom_message_command.format(user, user_display, user, message)))
                        t.start()

                    #message format for ltsp
                    else:
                        self.logger.debug('user_ip: ' + str(user_ip) + ' user_display: ' + str(user_display))
                        message_list = []
                        message_parser = message.split(" ")
                        self.logger.debug('running parser:--->> ' + str(message_parser))
                        for msg in message_parser:
                            message = '\\\ ' + str(msg)
                            message_list.append(message)
                            self.logger.debug('message_list:--->> ' + str(message_list))
                        message = ''.join(str(x) for x in message_list)
                        self.logger.debug('message: ' + str(message))
                        t = threading.Thread(target=self.execute(
                            self.custom_message_command_ltsp.format(user, user_display, user, message), ip=user_ip))
                        t.start()

        self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                     message='İşlem başarıyla gerçekleştirildi.',
                                     data=json.dumps({'Result': message}),
                                     content_type=ContentType.APPLICATION_JSON.value)


    def handle_task(self):
        try:
            message = self.data['message']
            self.logger.debug('[XMessage]: get message from lider: ' + str(message))
            selected_user = None

            if 'selected_user' in self.data:
                selected_user = str(self.data['selected_user'])
                self.logger.debug('[XMessage]: selected User: ' + str(selected_user))
                self.execute_user_message(selected_user, message)

            else:
                self.execute_xmessage(message)

        except Exception as e:
            self.logger.error(" error on handle xmessage task. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='XMessage mesajı olusturulurken hata oluştu:' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)


def handle_task(task, context):
    cls = RunXMessageCommand(task, context)
    cls.handle_task()
