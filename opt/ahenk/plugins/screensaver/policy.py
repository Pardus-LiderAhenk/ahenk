#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Mine Dogan <mine.dogan@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class Screensaver(AbstractPlugin):
    def __init__(self, data, context):
        super(Screensaver, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.logger.debug('Parameters were initialized.')

    def user_xscreen_conf_path(self, username):
        self.logger.debug('u1')
        user_home_path = self.execute('echo $( getent passwd "{0}" | cut -d: -f6 )'.format(username))[1]
        return '{0}/.xscreensaver'.format(user_home_path.strip())

    def create_content(self):
        data = json.loads(self.data)
        self.logger.debug('c1')
        return 'mode: {0}\ntimeout: {1}\ncycle: {2}\nlock: {3}\nlockTimeout: {4}\ngrabDesktopImages: {5}\n' \
               'grabVideoFrames: {6}\ndpmsEnabled: {7}\ndpmsStandby: {8}\ndpmsSuspend: {9}\ndpmsOff: {10}' \
               '\ndpmsQuickOff: {11}\ntextMode: {12}\ntextLiteral: {13}\ntextUrl: {14}\nfade: {15}\nunfade:' \
               ' {16}\nfadeSeconds: {17}\ninstallColormap: {18}\n'.format(data['mode'], data['timeout'],
                                                                           data['cycle'], data['lock'],
                                                                           data['lockTimeout'],
                                                                           data['grabDesktopImages'],
                                                                           data['grabVideoFrames'],
                                                                           data['dpmsEnabled'],
                                                                           data['dpmsStandby'],
                                                                           data['dpmsSuspend'],
                                                                           data['dpmsOff'],
                                                                           data['dpmsQuickOff'],
                                                                           data['textMode'],
                                                                           data['textLiteral'],
                                                                           data['textUrl'], data['fade'],
                                                                           data['unfade'],
                                                                           data['fadeSeconds'],
                                                                           data['installColormap'])

    def handle_policy(self):

        try:
            username = self.context.get('username')
            content = self.create_content()

            if username is not None:
                xfile_path = self.user_xscreen_conf_path(username)
                self.delete_file(xfile_path)
                self.write_file(xfile_path, content, 'w+')

                self.logger.debug('Config file content: \n{0}'.format(content))
                self.execute('chown {0}:{0} {1}'.format(username, xfile_path))
                self.logger.debug('.xscreensaver owner is changed.')
                self.logger.info('Screensaver profile is handled successfully for user.')

            else:
                for user in self.Sessions.user_name():
                    self.delete_file(self.user_xscreen_conf_path(user))
                    self.write_file(self.user_xscreen_conf_path(user), content, 'w+')
                # self.write_file('/etc/X11/app-defaults/XScreenSaver', content, 'w')
                self.logger.error('Screensaver profile is handled successfully for machine.')
            self.execute('xscreensaver-command -restart',as_user=self.context.get_username())
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value,
                                         message='Kullanıcı screensaver profili başarıyla çalıştırıldı.')

        except Exception as e:
            self.logger.error('A problem occured while handling screensaver profile: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value,
                                         message='Screensaver profili çalıştırılırken bir hata oluştu.')


def handle_policy(profile_data, context):
    screensaver = Screensaver(profile_data, context)
    screensaver.handle_policy()