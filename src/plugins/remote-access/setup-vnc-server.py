#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>
import json
import time
from base64 import b64encode
from os import urandom

from base.plugin.abstract_plugin import AbstractPlugin

class SetupVnc(AbstractPlugin):
    """docstring for SetupVnc"""

    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.password = self.create_password(10)
        self.port = self.get_port_number()
        self.logger.debug('Parameters were initialized')

    def handle_task(self):
        self.logger.debug('Handling task')
        try:
            self.run_vnc_server()
            self.logger.info('VNC Server running')
            ip_addresses = str(self.Hardware.Network.ip_addresses()).replace('[', '').replace(']', '').replace("'", '')

            self.data['port'] = self.port
            self.data['password'] = self.password
            self.data['host'] = ip_addresses
            self.logger.debug('Response data created')
            if self.data['permission'] == "yes":
                message = "VNC başarılı bir şekilde yapılandırıldı!\n{0} ip'li bilgisayara uzak erişim sağlanacaktır.\nKullanıcısının izni için lütfen bekleyiniz...'".format(self.data['host'])
            elif self.data['permission'] == "no":
                message = "VNC başarılı bir şekilde yapılandırıldı!\n{0} ip'li bilgisayara kullanıcı izni gerektirmeksizin uzak erişim sağlanmıştır...'".format(self.data['host'])
            else:
                message = "VNC başarılı bir şekilde yapılandırıldı!\n{0} ip'li bilgisayara kullanıcı izni ve bildirim gerektirmeksizin uzak erişim sağlanmıştır...'".format(self.data['host'])

            self.context.create_response(code=self.get_message_code().TASK_PROCESSED.value,
                                         message=message,
                                         data=json.dumps(self.data),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

        except Exception as e:
            self.logger.error('A problem occurred while running VNC server. Error Message: {}'.format(str(e)))
            self.context.create_response(code=self.get_message_code().TASK_ERROR.value,
                                         message='VNC sunucusu çalışırken bir hata oluştu.')

    def run_vnc_server(self):
        # user_name = self.db_service.select_one_result('session', 'username', " 1=1 order by id desc ")
        user_name = self.get_username()
        if user_name is None:
            user_name = self.get_active_user()
        self.logger.info('get logon username is {0}'.format(user_name))
        self.logger.debug('Is VNC server installed?')
        if self.is_installed('x11vnc') is False:
            self.logger.debug('VNC server not found, it is installing')
            self.install_with_apt_get('x11vnc')

        self.logger.debug('VNC server was installed')
        self.logger.debug('Killing running VNC proceses')
        self.execute("ps aux | grep x11vnc | grep 'port " + self.port + "' | awk '{print $2}' | xargs kill -9",
                     result=False)
        self.logger.debug('Running VNC proceses were killed')
        self.logger.debug('Getting display and username...')
        # display_number = self.get_username_display(user_name)
        display_number = self.Sessions.display(user_name)
        if display_number is None:
            display_number = self.get_username_display()
        desktop_env = self.get_desktop_env()
        if desktop_env == "gnome":
            display_number = self.get_username_display_gnome(user_name)
        self.logger.info("Get display of {0} is {1}".format(user_name, display_number))
        #homedir = self.get_homedir(user_name)
        #self.logger.info("Get home directory of {0} is {1}".format(user_name, homedir))
        # this user_name for execute method
        user_name = self.get_as_user()
        if user_name is None:
            user_name = self.get_active_user()
        self.logger.debug('Username:{0} Display:{1}'.format(user_name, display_number))
        #if self.is_exist('{0}/.vncahenk{1}'.format(homedir, user_name)) is True:
        #    self.delete_folder('{0}/.vncahenk{1}'.format(homedir, user_name))
        #    self.logger.debug('Cleaning previous configurations.')
        #self.logger.debug('Creating user VNC conf file as user')
        #self.execute('su - {0} -c "mkdir -p {1}/.vncahenk{0}"'.format(user_name, homedir), result=False)
        #self.logger.debug('Creating password as user')
        #self.execute('su - {0} -c "x11vnc -storepasswd {1} {2}/.vncahenk{3}/x11vncpasswd"'.format(user_name, self.password, homedir,user_name), result=False)
        self.logger.debug('Running VNC server as user.')
        if self.data['permission'] == "yes":
            self.execute('su - {0} -c "x11vnc -accept \'popup\' -gone \'popup\' -rfbport {1} -passwd {2} -capslock -display {3}"'.format(
                    user_name, self.port, self.password, display_number), result=False)
        elif self.data["permission"] == "no":
            self.logger.info("Lider Ahenk sistem yöneticisi 5 sn sonra bilgisayarınıza uzak erişim sağlayacaktır. ")
            # self.send_notify("Liderahenk",
            #                  "Lider Ahenk Sistem Yoneticisi tarafindan\n5 sn sonra bilgisayarınıza uzak erişim sağlanacaktır.\nBağlantı kapatıldıktan sonra ayrıca bilgilendirilecektir.",
            #                  display_number, user_name, timeout=50000)
            #time.sleep(2)
            self.execute('su - {0} -c "x11vnc -gone \'popup\' -rfbport {1} -passwd {2} -capslock -display {3}"'.format(
                    user_name, self.port, self.password, display_number), result=False)
        else:
            self.execute('su - {0} -c "x11vnc -rfbport {1} -passwd {2} -capslock -display {3}"'.format(
                    user_name, self.port, self.password, display_number), result=False)
            self.logger.info("Lider Ahenk sistem yöneticisi tarafından kullanıcı izni ve bildirim gerektirmeksizin uzak erişim sağlanmıştır")

    def create_password(self, pass_range):
        self.logger.debug('Password created')
        random_bytes = urandom(pass_range)
        return b64encode(random_bytes).decode('utf-8')

    def get_port_number(self):
        self.logger.debug('Target port is 5999')
        return '5999'

def handle_task(task, context):
    vnc = SetupVnc(task, context)
    vnc.handle_task()
