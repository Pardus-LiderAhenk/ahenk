#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin


class AddUser(AbstractPlugin):
    def __init__(self, task, context):
        super(AddUser, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.username = self.task['username']
        self.password = self.task['password']
        self.home = self.task['home']
        self.active = self.task['active']
        self.groups = self.task['groups']
        self.desktop_write_permission = self.task['desktop_write_permission']
        self.kiosk_mode = self.task['kiosk_mode']

        self.script = '/bin/bash ' + self.Ahenk.plugins_path() + 'local-user/scripts/{0}'

        self.add_user = 'useradd -d {0} {1}'
        self.check_home_owner = 'stat -c \'%U\' {}'
        self.enable_user = 'passwd -u {}'
        self.disable_user = 'passwd -l {}'
        self.add_user_to_groups = 'usermod -a -G {0} {1}'
        self.create_shadow_password = 'mkpasswd -m sha-512 {}'
        self.change_password = 'usermod -p {0} {1}'
        self.change_shell = 'usermod -s /bin/bash {}'
        self.change_owner = 'chown {0}.{0} {1}'
        self.change_permission = 'chmod 755 {}'

        self.desktop_path = ''
        self.logger.debug('Parameters were initialized.')

    def handle_task(self):
        try:
            if not self.is_exist(self.home):
                self.create_directory(self.home)
            self.execute(self.add_user.format(self.home, self.username))
            self.logger.debug('Added new user: {0}, home: {1}'.format(self.username, self.home))

            self.execute(self.change_owner.format(self.username, self.home))
            self.execute(self.change_permission.format(self.home))
            self.logger.debug('Changed owner and permission for home directory.')

            if self.groups != "":
                self.execute(self.add_user_to_groups.format(self.groups, self.username))
                self.logger.debug('Added user to these groups: {}'.format(self.groups))

            if str(self.password).strip() != "":
                result_code, p_out, p_err = self.execute(self.create_shadow_password.format(self.password))
                shadow_password = p_out.strip()
                self.execute(self.change_password.format('\'{}\''.format(shadow_password), self.username))
                self.logger.debug('Changed password.')

            self.execute(self.change_shell.format(self.username))
            self.logger.debug('Changed user shell to /bin/bash')

            if self.active == "true":
                self.execute(self.enable_user.format(self.username))
                self.logger.debug('The user has been enabled.')
            elif self.active == "false":
                self.execute(self.disable_user.format(self.username))
                self.logger.debug('The user has been disabled.')

            self.execute("mkdir " + self.home + "/Masaüstü")
            self.desktop_path = self.home + "/Masaüstü"

            if self.desktop_write_permission == "true":
                self.execute('chown -R {0}:{1} {2}'.format(self.username, self.username, self.desktop_path))
                self.logger.debug('chown -R {0}:{1} {2}'.format(self.username, self.username, self.desktop_path))

            elif self.desktop_write_permission == "false":
                self.execute('chown -R root:root {0}'.format(self.desktop_path))
                self.logger.debug('chown -R root:root {0}'.format(self.desktop_path))

            #
            # Handle kiosk mode
            #
            result_code, p_out, p_err = self.execute(self.script.format('find_locked_users.sh'), result=True)
            if result_code != 0:
                self.logger.error(
                    'Error occurred while managing kiosk mode.')
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                     message='Masaüstü kilidi ayarlanırken hata oluştu.')
                return
            locked_users = []
            if p_out:
                self.logger.debug('pout {0}'.format(str(p_out)))
                locked_users = p_out.strip().split(';')
            if self.kiosk_mode == "true":
                self.logger.debug('Kiosk mode is active {0}'.format(str(locked_users)))
                if self.username not in locked_users:
                    self.logger.debug('Adding user {0} to locked users'.format(self.username))
                    locked_users.append(self.username)
                locked_users_str = ";".join(locked_users)
                self.logger.debug('Users: {0}'.format(locked_users_str))
                comm = "sed -i 's/^.*" + '<channel name="xfce4-panel"' + ".*$/" + '<channel name="xfce4-panel" version="1.0" locked="' + locked_users_str + '">' + "/' /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml"
                result_code1, p_out1, p_err1 = self.execute(comm)
            elif self.kiosk_mode == "false":
                self.logger.debug('Kiok mode is NOT active')
                if self.username in locked_users:
                    self.logger.debug('Removing user {0} from locked users'.format(self.username))
                    locked_users.remove(self.username)
                if locked_users:
                    locked_users_str = ";".join(locked_users)
                    comm = "sed -i 's/^.*" + '<channel name="xfce4-panel"' + ".*$/" + '<channel name="xfce4-panel" version="1.0" locked="' + locked_users_str + '">' + "/' /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml"
                    result_code1, p_out1, p_err1 = self.execute(comm)
                else:
                    self.execute(self.script.format('remove_locked_users.sh '))

            self.logger.info('User has been added successfully.')

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Kullanıcı başarıyla eklendi.')



        except Exception as e:
            self.logger.error('A problem occurred while handling Local-User task: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Local-User görevi çalıştırılırken bir hata oluştu.')


def handle_task(task, context):
    add_user = AddUser(task, context)
    add_user.handle_task()
