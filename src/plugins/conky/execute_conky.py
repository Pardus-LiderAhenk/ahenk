#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Edip YILDIZ


from base.model.enum.content_type import ContentType
import json

from base.plugin.abstract_plugin import AbstractPlugin


class RunConkyCommand(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.conky_config_file_dir = '/etc/conky'
        self.conky_config_global_autorun_file = '/etc/xdg/autostart/conky.desktop'
        self.conky_config_file_path = self.conky_config_file_dir + '/conky.conf'
        self.logger.debug('[Conky] Parameters were initialized.')
        self.conky_autorun_content = '[Desktop Entry] \n' \
                                     'Comment[tr]= \n' \
                                     'Comment= \n' \
                                     'Exec=conky_wp \n' \
                                     'GenericName[tr]= \n' \
                                     'GenericName= \n' \
                                     'Icon=system-run \n' \
                                     'MimeType= \n' \
                                     'Name[tr]= \n' \
                                     'Name= \n' \
                                     'Path= \n' \
                                     'StartupNotify=true \n' \
                                     'Terminal=false \n' \
                                     'TerminalOptions= \n' \
                                     'Type=Application \n' \
                                     'X-DBUS-ServiceName= \n' \
                                     'X-DBUS-StartupType= \n' \
                                     'X-KDE-SubstituteUID=false \n' \
                                     'X-KDE-Username= \n'

        self.conky_wrapper_file= '/usr/bin/conky_wp'

        self.conky_wrapper_content = '#!/bin/bash \n' \
                                  ' killall conky \n' \
                                  ' sleep 5 \n' \
                                  ' /usr/bin/conky -q \n'

    def remove_conky_message(self):
        self.execute("killall conky")
        if self.is_exist(self.conky_config_global_autorun_file) == True:
            self.delete_file(self.conky_config_global_autorun_file)

        self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                     message='Conky measajları kaldırıldı',
                                     content_type=ContentType.APPLICATION_JSON.value)


    def execute_conky(self, conky_message):
        self.logger.debug("[CONKY] Executing conky.")
        try:
            if self.is_installed('conky') is False:
                self.logger.info('[Conky] Could not found Conky. It will be installed')
                self.logger.debug('[Conky] Conky installing with using apt-get')
                self.install_with_apt_get('conky')
                self.logger.info('[Conky] Could installed')

            self.logger.debug('[Conky] Some processes found which names are conky. They will be killed.')
            self.execute('killall conky')

        except:
            self.logger.error('[Conky] Conky install-kill problem.')
            raise

        if self.is_exist(self.conky_config_file_dir) == False:
            self.logger.debug('[Conky] Creating directory for conky config at ' + self.conky_config_file_dir)
            self.create_directory(self.conky_config_file_dir)

        if self.is_exist(self.conky_config_file_path) == True:
            self.logger.debug('[Conky] Old config file will be renamed.')
            self.rename_file(self.conky_config_file_path, self.conky_config_file_path + '_old')
            self.logger.debug('[Conky] Old config file will be renamed to ' + (self.conky_config_file_path + 'old'))

        self.create_file(self.conky_config_file_path)
        self.write_file(self.conky_config_file_path, conky_message)
        self.logger.debug('[Conky] Config file was filled by context.')


        # creating wrapper file if is not exist. wrapper for using conky command..its need for ETA
        if self.is_exist(self.conky_wrapper_file) == False:
            self.logger.debug('[Conky] Creating directory for conky wrapper file at ' + self.conky_wrapper_file)
            self.create_file(self.conky_wrapper_file)
            self.write_file(self.conky_wrapper_file,self.conky_wrapper_content)

        if self.is_exist(self.conky_wrapper_file) == True:
            self.execute('chmod +x ' + self.conky_wrapper_file)

        # creating autorun file if is not exist
        if self.is_exist(self.conky_config_global_autorun_file) == False:
            self.logger.debug('[Conky] Creating directory for conky autorun file at ' + self.conky_config_global_autorun_file)
            self.create_file(self.conky_config_global_autorun_file)
            self.write_file(self.conky_config_global_autorun_file, self.conky_autorun_content)

        users = self.Sessions.user_name()
        desktop_env = self.get_desktop_env()
        self.logger.info("Get desktop environment is {0}".format(desktop_env))

        for user in users:
            user_display = self.Sessions.display(user)
            if desktop_env == "gnome":
                user_display = self.get_username_display_gnome(user)

            if user_display is None:
                self.logger.debug('[Conky] executing for display none for user  '+ str(user))
                self.execute('conky -q', result=False)
            else:
                self.logger.debug('[Conky] user display ' + str(user_display) +' user '+ str(user))
                conky_cmd = 'su ' + str(user) + ' -c ' + ' "conky --display=' + str(user_display) + ' " '
                self.logger.debug('[Conky] executing command:  ' + str(conky_cmd))
                self.execute(conky_cmd, result=False)


        #self.execute('conky ', result=False)

        self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                     message='Conky başarıyla oluşturuldu.',
                                     data=json.dumps({'Result': conky_message}),
                                     content_type=ContentType.APPLICATION_JSON.value)

    def handle_task(self):
        try:
            conky_message = self.data['conkyMessage']
            remove_conky_message = self.data['removeConkyMessage']

            if remove_conky_message:
                self.remove_conky_message()

            else:
                self.execute_conky(conky_message)

        except Exception as e:
            self.logger.error(" error on handle conky task. Error: " + str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Conky mesajı olusturulurken hata oluştu:' + str(e),
                                         content_type=ContentType.APPLICATION_JSON.value)


def handle_task(task, context):
    cls = RunConkyCommand(task, context)
    cls.handle_task()
