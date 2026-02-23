#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

import json
from os import urandom
from base.plugin.abstract_plugin import AbstractPlugin
from base64 import b64encode
from base.util.display_helper import DisplayServerType, DisplayHelper


class SetupRDPServer(AbstractPlugin):
    """Setup RDP Server for GNOME"""

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()

        self.password = self.generate_password()
        self.port = 3389
        self.permission = self.data.get('permission')


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
            
            session = DisplayServerType.detect_desktop_env()

            env_string = DisplayHelper.build_env_string(
                desktop_server_type=session,
                user=username
            )
            if self.permission == "yes":
                command = (
                    f"su {username} -c \"{env_string} "
                    f"zenity --question --width=400 --height=200 "
                    f"--title 'Liderahenk Uzak Erişim' --text 'Liderahenk sistem yöneticisi tarafından uzak erişim başlatılacaktır. Onaylıyor musunuz?'\""
                )
                result_code, p_out, p_err = self.execute(command)

                if result_code != 0:
                    self.context.create_response(
                        code=self.get_message_code().TASK_ERROR.value,
                        message='Kullanıcı uzak erişim izni vermedi.',
                        content_type=self.get_content_type().APPLICATION_JSON.value
                    )
                    return


            # Apply credentials, port and enable RDP as the target user
            # password wrapped in single quotes (base64 output does not contain single quote)
            cmd = (
                f"su - {username} -c \""
                f"grdctl rdp set-credentials {username} '{self.password}' "
                f"&& grdctl rdp set-port {self.port} "
                f"&& grdctl rdp disable-view-only "
                f"&& grdctl rdp enable\""
            )

            self.logger.info("Enabling RDP with grdctl")
            self.execute(cmd, result=False)

            ip_addresses = ", ".join(self.Hardware.Network.ip_addresses())

            self.data.update({
                'port': self.port,
                'password': self.password,
                'host': ip_addresses,
                'username': self.get_active_local_user(),
                'protocol': 'rdp'
            })


            if self.permission == "yes":
                msg = "Kullanıcı izni istenerek uzak erişim başlatıldı."
            elif self.permission == "no":
                msg = "Kullanıcı izni olmadan uzak erişim başlatıldı."
            else:
                msg = "Sessiz uzak erişim başlatıldı."

            self.context.create_response(
                code=self.get_message_code().TASK_PROCESSED.value,
                message=f"RDP hazır. {msg}",
                data=json.dumps(self.data),
                content_type=self.get_content_type().APPLICATION_JSON.value
            )

        except Exception as e:
            self.logger.error("RDP task failed")
            self.context.create_response(
                code=self.get_message_code().TASK_ERROR.value,
                message='RDP sunucusu çalışırken hata oluştu.'
            )

    def create_password(self, pass_range):
        self.logger.debug(f'Creating password with range: {pass_range}')
        password = b64encode(urandom(pass_range)).decode('utf-8').replace('+', '').replace('/', '').replace('=', '')
        self.logger.debug('Password created successfully')
        return password

    def generate_password(self):
        return str(urandom(16).hex())


def handle_task(task, context):
    SetupRDPServer(task, context).handle_task()
