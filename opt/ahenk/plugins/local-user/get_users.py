#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json

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
        self.desktop_path = '/home/agem/Masaüstü'

        self.logger.debug('Parameters were initialized.')

    def handle_task(self):

        try:
            user_list = []

            result_code, p_out, p_err = self.execute(self.command_users)
            lines = p_out.split('\n')
            lines.pop()

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

                is_desktop_write_permission_exists = 'false'
                self.logger.debug("sudo -u " + str(detail[0]).strip() + " touch -c " + self.desktop_path + " 2>&1 | grep 'Permission denied'")
                result_code, p_out, p_err = self.execute(" touch -c " + self.desktop_path + " 2>&1 | grep 'Permission denied'", as_user=str(detail[0]).strip())
                self.logger.debug("result codeee : " + str(result_code).strip())
                if result_code == 1:
                    is_desktop_write_permission_exists = 'true'

                is_kiosk_mode_on = 'false'
                self.logger.debug('Kiosk mode info will be taken')
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
                self.logger.debug('Kiosk mode info is taken')

                user = {'user': str(detail[0]).strip(), 'groups': groups[1], 'home': detail[1], 'is_active': is_active, 'is_desktop_write_permission_exists': is_desktop_write_permission_exists, 'is_kiosk_mode_on': is_kiosk_mode_on}
                user_list.append(user)

                self.logger.debug(
                    'user: {0}, groups: {1}, home: {2}, is_active: {3}'.format(str(detail[0]).strip(), groups[1],
                                                                               detail[1], is_active))

            self.logger.info('Local User task is handled successfully')
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Kullanıcı listesi başarıyla getirildi.',
                                         data=json.dumps({'users': user_list}),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occurred while handling Local-User task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Local-User görevi çalıştırılırken bir hata oluştu.')


def handle_task(task, context):
    get_users = GetUsers(task, context)
    get_users.handle_task()
