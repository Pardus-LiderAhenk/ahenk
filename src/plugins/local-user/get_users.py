#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>
# Author:Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

import json
from pathlib import Path

from base.plugin.abstract_plugin import AbstractPlugin

class GetUsers(AbstractPlugin):
    def __init__(self, task, context):
        super(GetUsers, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.script = '/bin/bash ' + self.Ahenk.plugins_path() + 'local-user/scripts/{0}'

        self.command_users = 'awk -F: \'{print $1 ":" $6 ":" $7}\' /etc/passwd | grep /bin/bash'
        self.command_user_groups = 'groups {}'
        self.command_not_active = 'egrep \':\!\' /etc/shadow |awk -F: \'{print $1}\''
        self.command_get_groups = 'cut -d: -f1 /etc/group'
        self.xfce4_session = "/usr/bin/xfce4-session"
        self.gnome_session = "/usr/bin/gnome-session"
        self.desktop_env = None
        self.logger.debug('Parameters were initialized.')

    def handle_task(self):

        try:
            user_list = []
            result_code, p_out, p_err = self.execute(self.command_users)
            lines = p_out.split('\n')
            lines.pop()

            self.desktop_env = self.get_desktop_env()
            self.logger.info("Get desktop environment is {0}".format(self.desktop_env))

            for line in lines:
                detail = line.split(':')

                result_code, p_out, p_err = self.execute(self.command_user_groups.format(str(detail[0]).strip()))
                groups = p_out.split(':')
                groups[1] = str(groups[1]).strip()
                groups[1] = groups[1].replace("'", "").replace(" ", ", ")
                is_active = 'true'
                result_code, p_out, p_err = self.execute(self.command_not_active)
                users = p_out.split('\n')

                if str(detail[0]).strip() in users:
                    is_active = 'false'

                self.desktop_path = ''
                if self.is_exist("{0}/Masaüstü/".format(str(detail[1]).strip())):
                    self.desktop_path = "{0}/Masaüstü/".format(str(detail[1]).strip())
                    self.logger.debug("Desktop path for user '{0}' : {1}".format(str(detail[0]).strip(), self.desktop_path))
                elif self.is_exist("{0}/Desktop/".format(str(detail[1]).strip())):
                    self.desktop_path = "{0}/Desktop/".format(str(detail[1]).strip())
                    self.logger.debug("Desktop path for user '{0}' : {1}".format(str(detail[0]).strip(), self.desktop_path))
                else:
                    self.logger.debug(
                        'Desktop write permission could not get. Desktop path not found for user "{0}"'.format(
                            str(detail[0]).strip()))

                result_code, p_out, p_err = self.execute(' stat -c "%a %n" ' + self.desktop_path)
                self.logger.debug('sudo stat -c "%a %n" ' + self.desktop_path)
                is_desktop_write_permission_exists = 'false'
                if result_code == 0:
                    permission_codes = p_out.split()
                    self.logger.debug("permission codes : " + str(permission_codes))
                    if len(permission_codes) > 0:
                        permission_code = permission_codes[0].strip()
                        self.logger.debug("permission code is : " + permission_code)
                        if permission_code == "775":
                            is_desktop_write_permission_exists = 'true'

                if self.desktop_env == "xfce":
                    is_kiosk_mode_on = 'false'
                    self.logger.debug('Kiosk mode info will be taken')
                    file_xfce4_panel = Path("/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml")
                    if not file_xfce4_panel.exists():
                        self.logger.error(
                            'PANEL XML NOT FOUND COPY')
                        source_path = "{0}local-user/panelconf/xfce4-panel.xml".format(self.Ahenk.plugins_path())
                        self.logger.info("----->>>>" + source_path)
                        self.copy_file(source_path, "/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml")
                        self.logger.error(
                            'FILE IS COPIED')
                    result_code, p_out, p_err = self.execute(self.script.format('find_locked_users.sh'), result=True)
                    if result_code != 0:
                        self.logger.error(
                            'Error occurred while finding locked users.')
                    if p_out:
                        self.logger.debug('locked users are {0}'.format(str(p_out)))
                        locked_users = p_out.strip().split(';')
                        # self.logger.debug("user is " + str(detail[0]).strip())
                        # self.logger.debug("locked users are " + str(locked_users))
                        if str(detail[0]).strip() in locked_users:
                            is_kiosk_mode_on = 'true'
                    self.logger.debug('Desktop environ is XFCE. Kiosk mode info is taken')
                else:
                    is_kiosk_mode_on = "true"
                    self.logger.info("Desktop environ is GNOME. Return kiok mode TRUE")

                user = {'user': str(detail[0]).strip(), 'groups': groups[1], 'home': detail[1], 'is_active': is_active, 'is_desktop_write_permission_exists': is_desktop_write_permission_exists, 'is_kiosk_mode_on': is_kiosk_mode_on}
                user_list.append(user)
                self.logger.debug('user: {0}, groups: {1}, home: {2}, is_active: {3}'.format(str(detail[0]).strip(), groups[1], detail[1], is_active))
            self.logger.info('Local User task is handled successfully')
            #
            # get all groups
            #
            result_code, p_out, p_err = self.execute(self.command_get_groups)
            all_groups = p_out.split('\n')
            all_groups.pop()

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Kullanıcı listesi başarıyla getirildi.',
                                         data=json.dumps({'users': user_list, 'all_groups': all_groups}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occurred while handling Local-User task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Local-User görevi çalıştırılırken bir hata oluştu.')


def handle_task(task, context):
    get_users = GetUsers(task, context)
    get_users.handle_task()
