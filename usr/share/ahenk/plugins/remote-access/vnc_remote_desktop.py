#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

import json
from os import urandom
from base.plugin.abstract_plugin import AbstractPlugin
from base64 import b64encode
from base.util.display_helper import DisplayHelper, DisplayServerType


class SetupXfceVnc(AbstractPlugin):
    """Setup VNC Server for XFCE"""

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()

        self.password = self.create_password(10)
        self.port = "5999"


    def handle_task(self):
        self.logger.debug('Handling task')
        try:
            username = self.get_active_local_user()
            self.logger.info(f'Active user: {username}')

            if not username:
                self.context.create_response(
                    code=self.get_message_code().TASK_ERROR.value,
                    message='Display bulunamadı: Oturum açmış kullanıcı yok.',
                    content_type=self.get_content_type().APPLICATION_JSON.value
                )
                return
            display = DisplayHelper.detect_user_display(username)
            session = DisplayServerType.detect_desktop_env()
            permission = self.data.get('permission')
            env_string = DisplayHelper.build_env_string(
                desktop_server_type=session,
                user=username
            )
            if permission == "yes":
                question_command = (
                    f"su {username} -c \"{env_string} "
                    f"zenity --question --width=400 --height=200 "
                    f"--title 'Liderahenk Uzak Erişim' --text 'Liderahenk sistem yöneticisi tarafından uzak erişim başlatılacaktır. Onaylıyor musunuz?'\""
                )
                result_code, p_out, p_err = self.execute(question_command)

                if result_code != 0:
                    self.context.create_response(
                        code=self.get_message_code().TASK_ERROR.value,
                        message='Kullanıcı uzak erişim izni vermedi.',
                        content_type=self.get_content_type().APPLICATION_JSON.value
                    )
                    return


            kill_cmd = (
                f"ps aux | grep '[x]11vnc' | grep 'rfbport {self.port}' "
                f"| awk '{{print $2}}' | xargs -r kill -9"
            )
            self.execute(kill_cmd, result=False)

            home_dir = self.get_homedir(username)
            passwd_file = f"{home_dir}/.vnc/passwd"
            self.execute(
                f"su - {username} -c \"mkdir -p ~/.vnc && x11vnc -storepasswd {self.password} {passwd_file}\"",
                result=False
            )

            command = (
                f"su - {username} -c \""
                f"x11vnc "
                f"-display {display} "
                f"-rfbport {self.port} "
                f"-rfbauth {passwd_file} "
                f"-bg "
                f"-capslock "
                f"-gone 'popup'\""
            )

            self.logger.info("Starting x11vnc server")
            self.execute(command, result=False)

            ip_addresses = ", ".join(self.Hardware.Network.ip_addresses())

            self.data.update({
                'port': self.port,
                'password': self.password,
                'host': ip_addresses,
                'protocol': 'vnc'
            })

            if permission == "yes":
                msg = "Kullanıcı izni istenerek uzak erişim başlatıldı."
            elif permission == "no":
                msg = "Kullanıcı izni olmadan uzak erişim başlatıldı."
            else:
                msg = "Sessiz uzak erişim başlatıldı."

            self.context.create_response(
                code=self.get_message_code().TASK_PROCESSED.value,
                message=f"VNC hazır. {msg}",
                data=json.dumps(self.data),
                content_type=self.get_content_type().APPLICATION_JSON.value
            )

        except Exception as e:
            self.logger.error("VNC task failed" + str(e))
            self.context.create_response(
                code=self.get_message_code().TASK_ERROR.value,
                message='VNC sunucusu çalışırken hata oluştu.'
            )

    def create_password(self, pass_range):
        self.logger.debug('Password created')
        return b64encode(urandom(pass_range)).decode('utf-8')


def handle_task(task, context):
    SetupXfceVnc(task, context).handle_task()
