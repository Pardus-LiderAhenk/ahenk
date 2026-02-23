#!/usr/bin/python3
# -*- coding: utf-8 -*-

from base.model.enum.content_type import ContentType
import json
from base.plugin.abstract_plugin import AbstractPlugin
from base.util.display_helper import DisplayHelper, DisplayServerType

class RunConkyCommand(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        
        # Configuration paths
        self.conky_config_file_dir = '/etc/conky'
        self.conky_config_global_autorun_file = '/etc/xdg/autostart/conky.desktop'
        self.conky_config_file_path = f'{self.conky_config_file_dir}/conky.conf'
        
        self.logger.debug('[Conky] Parameters were initialized.')
        
        # Autorun content
        self.conky_autorun_content = (
            '[Desktop Entry] \n'
            'Comment[tr]= \n'
            'Comment= \n'
            'Exec=conky_wp \n'
            'GenericName[tr]= \n'
            'GenericName= \n'
            'Icon=system-run \n'
            'MimeType= \n'
            'Name[tr]= \n'
            'Name= \n'
            'Path= \n'
            'StartupNotify=true \n'
            'Terminal=false \n'
            'TerminalOptions= \n'
            'Type=Application \n'
            'X-DBUS-ServiceName= \n'
            'X-DBUS-StartupType= \n'
            'X-KDE-SubstituteUID=false \n'
            'X-KDE-Username= \n'
        )
        
        self.conky_wrapper_file = '/usr/bin/conky_wp'
        self.conky_wrapper_content = (
            '#!/bin/bash \n'
            'killall conky \n'
            'sleep 5 \n'
            '/usr/bin/conky -q \n'
        )

    def remove_conky_message(self):
        self.execute("killall conky")
        if self.is_exist(self.conky_config_global_autorun_file):
            self.delete_file(self.conky_config_global_autorun_file)
        
        self.context.create_response(
            code=self.message_code.TASK_PROCESSED.value,
            message='Conky mesajları kaldırıldı',
            content_type=ContentType.APPLICATION_JSON.value
        )

    def execute_conky(self, conky_message):
        self.logger.debug("[CONKY] Executing conky.")

        username = self.get_active_local_user()
        user_display = DisplayHelper.detect_user_display(username)

        if username is None or user_display is None:
            self.logger.warning('[Conky] No display found: No logged-in user.')
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message='Display bulunamadı: Oturum açmış kullanıcı yok.',
                content_type=ContentType.APPLICATION_JSON.value
            )
            return
        
        if DisplayServerType.detect_desktop_env() == DisplayServerType.WAYLAND.value:
            self.logger.warning('[Conky] Wayland display server detected. Conky is not supported on Wayland.')
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message='Conky Wayland display sunucusunda desteklenmiyor.',
                content_type=ContentType.APPLICATION_JSON.value
            )
            return

        self.execute('killall conky')

        # Create configuration directory if it doesn't exist
        if not self.is_exist(self.conky_config_file_dir):
            self.logger.debug(f'[Conky] Creating directory: {self.conky_config_file_dir}')
            self.create_directory(self.conky_config_file_dir)

        # Rename old config file if it exists
        if self.is_exist(self.conky_config_file_path):
            self.logger.debug('[Conky] Renaming old config file.')
            self.rename_file(self.conky_config_file_path, f'{self.conky_config_file_path}_old')

        # Create and write new config file
        self.create_file(self.conky_config_file_path)
        self.write_file(self.conky_config_file_path, conky_message)
        self.logger.debug('[Conky] Config file updated.')

        # Create wrapper file if it doesn't exist
        if not self.is_exist(self.conky_wrapper_file):
            self.logger.debug(f'[Conky] Creating wrapper file: {self.conky_wrapper_file}')
            self.create_file(self.conky_wrapper_file)
            self.write_file(self.conky_wrapper_file, self.conky_wrapper_content)
            self.execute(f'chmod +x {self.conky_wrapper_file}')

        # Create autorun file if it doesn't exist
        if not self.is_exist(self.conky_config_global_autorun_file):
            self.logger.debug(f'[Conky] Creating autorun file: {self.conky_config_global_autorun_file}')
            self.create_file(self.conky_config_global_autorun_file)
            self.write_file(self.conky_config_global_autorun_file, self.conky_autorun_content)

        
        # Execute conky command
        if user_display is None:
            self.logger.debug(f'[Conky] Executing for display none for user: {username}')
            self.execute('conky -q', result=False)
        else:
            self.logger.debug(f'[Conky] Executing command for user display: {user_display}')
            as_user = self.get_as_user()
            conky_cmd = f'su {as_user} -c "conky --display={user_display}"'
            self.logger.debug(f'[Conky] Executing command: {conky_cmd}')
            self.execute(conky_cmd, result=False)

        self.context.create_response(
            code=self.message_code.TASK_PROCESSED.value,
            message='Conky başarıyla oluşturuldu.',
            data=json.dumps({'Result': conky_message}),
            content_type=ContentType.APPLICATION_JSON.value
        )

    def handle_task(self):

        try:
            conky_message = self.data['conkyMessage']
            remove_conky_message = self.data['removeConkyMessage']
            if remove_conky_message:
                self.remove_conky_message()
            else:
                 # Check if Wayland is being used
               
                self.execute_conky(conky_message)
        except Exception as e:
            self.logger.error(f"Error handling conky task: {e}")
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message=f'Conky mesajı oluşturulurken hata oluştu: {e}',
                content_type=ContentType.APPLICATION_JSON.value
            )

def handle_task(task, context):
    cls = RunConkyCommand(task, context)
    cls.handle_task()
