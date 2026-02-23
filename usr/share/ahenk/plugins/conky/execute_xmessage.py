#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from base.model.enum.content_type import ContentType
from base.plugin.abstract_plugin import AbstractPlugin
from base.util.display_helper import DisplayHelper, DisplayServerType


class RunXMessageCommand(AbstractPlugin):

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()


    def execute_xmessage(self, message):
        """Executes zenity info window for active user"""
        user = self.get_active_local_user()
        self.logger.info(f"USER: {user}")

        session = DisplayServerType.detect_desktop_env()
        display = DisplayHelper.detect_user_display(user)

        if user is None or display is None:
            self.logger.info(f"No display found for user={user}")
            return "no_display"

        env_string = DisplayHelper.build_env_string(
            desktop_server_type=session,
            user=user
        )

        title = "Liderahenk Bildiri"
        content = message

        command = (
            f"su {user} -c \"{env_string} "
            f"zenity --info --width=400 --height=200 "
            f"--title '{title}' --text '{content}'\""
        )

        self.execute(command, detach=True)

        self.context.create_response(
            code=self.message_code.TASK_PROCESSED.value,
            message='İşlem başarıyla gerçekleştirildi.',
            data=json.dumps({'Result': message}),
            content_type=ContentType.APPLICATION_JSON.value
        )

    def handle_task(self):
        """Main task handler"""
        try:
            message = self.data['message']
            result = self.execute_xmessage(message)

            if result == "no_display":
                self.logger.error("No display found for showing message window.")
                self.context.create_response(
                    code=self.message_code.TASK_ERROR.value,
                    message='Display bulunamadı: Oturum açmış kullanıcı yok.',
                    content_type=ContentType.APPLICATION_JSON.value
                )
                return

            self.context.create_response(
                code=self.message_code.TASK_PROCESSED.value,
                message='İşlem başarıyla gerçekleştirildi.',
                data=json.dumps({'Result': message}),
                content_type=ContentType.APPLICATION_JSON.value
            )

        except Exception as e:
            self.logger.error(f"Error on handle xmessage task: {str(e)}")
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message='Liderahenk mesajı oluşturulurken hata oluştu: ' + str(e),
                content_type=ContentType.APPLICATION_JSON.value
            )


def handle_task(task, context):
    xmessage = RunXMessageCommand(task, context)
    xmessage.handle_task()
