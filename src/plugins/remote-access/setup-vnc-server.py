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

        users = self.Sessions.user_name()
        self.logger.debug('[XMessage] users : ' + str(users))

        for user in users:
            user_display = self.Sessions.display(user)

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

            arr = self.get_username_display()

            if len(arr) < 1:
                raise NameError('Display not found!')

            params = str(arr[0]).split(' ')

            self.logger.info("--------->>>> "+str(params))

            self.logger.debug('Username:{0} Display:{1}'.format(params[0], params[1]))

            if self.is_exist('/home/{0}/.vncahenk{0}'.format(params[0])) is True:
                self.logger.debug('Cleaning previous configurations.')
                # self.delete_folder('/home/{0}/.vncahenk{0}'.format(params[0]))

            self.logger.debug('Creating user VNC conf file as user')
            self.execute('su - {0} -c "mkdir -p /home/{0}/.vncahenk{1}"'.format(params[0], params[0]), result=False)

            self.logger.debug('Creating password as user')
            self.execute('su - {0} -c "x11vnc -storepasswd {1} /home/{0}/.vncahenk{2}/x11vncpasswd"'.format(params[0], self.password, params[0]), result=False)

            self.logger.debug('Running VNC server as user.')

            if self.data['permission'] == "yes":
                self.send_notify("Liderahenk", "Lider Ahenk Sistem Yoneticisi tarafindan\n5 sn sonra bilgisayarınıza uzak erişim sağlanacaktır.\nBağlantı kapatıldıktan sonra ayrıca bilgilendirilecektir.",":0", params[0], timeout=50000)
                time.sleep(5)

                self.execute('su - {0} -c "x11vnc -accept \'popup\' -gone \'popup\' -rfbport {1} -rfbauth /home/{0}/.vncahenk{2}/x11vncpasswd -o /home/{0}/.vncahenk{3}/vnc.log -display :{4}"'.format(
                        params[0], self.port, params[0], params[0], params[1]), result=False)
            elif self.data["permission"] == "no":

                self.logger.info("Lider Ahenk sistem yöneticisi 5 sn sonra bilgisayarınıza uzak erişim sağlayacaktır. ")

                self.send_notify("Liderahenk", "Lider Ahenk Sistem Yoneticisi tarafindan\n5 sn sonra bilgisayarınıza uzak erişim sağlanacaktır.\nBağlantı kapatıldıktan sonra ayrıca bilgilendirilecektir.", ":0", params[0], timeout=50000)
                time.sleep(5)

                self.execute('su - {0} -c "x11vnc -gone \'popup\' -rfbport {1} -rfbauth /home/{0}/.vncahenk{2}/x11vncpasswd -o /home/{0}/.vncahenk{3}/vnc.log -display :{4}"'.format(
                        params[0], self.port, params[0], params[0], params[1]), result=False)

            else:
                self.execute(
                    'su - {0} -c "x11vnc -rfbport {1} -rfbauth /home/{0}/.vncahenk{2}/x11vncpasswd -o /home/{0}/.vncahenk{3}/vnc.log -display :{4}"'.format(
                        params[0], self.port, params[0], params[0], params[1]), result=False)
                self.logger.info("Lider Ahenk sistem yöneticisi tarafından kullanıcı izni ve bildirim gerektirmeksizin uzak erişim sağlanmıştır")

    def get_username_display(self):
        result_code, p_out, p_err = self.execute("who | awk '{print $1, $5}' | sed 's/(://' | sed 's/)//'", result=True)

        self.logger.debug('Getting display result code:{0}'.format(str(result_code)))

        result = []
        lines = str(p_out).split('\n')
        for line in lines:
            arr = line.split(' ')
            if len(arr) > 1 and str(arr[1]).isnumeric() is True:
                result.append(line)
        return result

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

