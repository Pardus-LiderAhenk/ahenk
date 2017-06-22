#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Mine DOGAN <mine.dogan@agem.com.tr>
# Author: Emre Akkaya <emre.akkaya@agem.com.tr>


from base.plugin.abstract_plugin import AbstractPlugin
import json
import traceback


class TakeScreenshot(AbstractPlugin):
    def __init__(self, data, context):
        super(TakeScreenshot, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.temp_file_name = str(self.generate_uuid())
        self.shot_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)
        self.take_screenshot = 'xwd -root -display :{0} | convert  - jpg:- > ' + self.shot_path

    def handle_task(self):
        try:
            user_name = None

            if self.has_attr_json(self.data, self.Ahenk.dn()) and self.data[self.Ahenk.dn()] is not None:
                user_name = self.data[self.Ahenk.dn()]

            if not user_name:
                self.logger.debug('Taking screenshot with default display.')
                arr = self.get_username_display()
                self.logger.debug('Default username: {0} display: {1}'.format(arr[0], arr[1]))
                if arr is None:
                    self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                 message='Ekran görüntüsü alırken hata oluştu: Varsayılan display\'e erişilemedi.')
                    return

                ##permission
                self.logger.debug(
                    'Asking for screenshot to user {0} on {1} display'.format(arr[0], arr[1]))

                user_answer = self.ask_permission(':'+arr[1], arr[0],
                                                  "Ekran görüntüsünün alınmasına izin veriyor musunuz?",
                                                  "Ekran Görüntüsü")

                if user_answer is None:
                    self.logger.error('User answer could not kept.')
                    self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                 message='Ekran görüntüsü alırken hata oluştu: Kullanıcı iznine erişilemedi.')
                    return
                elif user_answer is True:
                    self.logger.debug('User accepted for screenshot')
                    self.logger.debug('Taking screenshot with specified display: {0}'.format(arr[1]))
                    self.logger.debug(
                        'Executing take screenshot command with user: {0} and display: {1}'.format(arr[0], arr[1]))
                    self.logger.debug(str(self.take_screenshot.format(arr[1])))
                    result_code, p_out, p_err = self.execute(self.take_screenshot.format(arr[1]), as_user=arr[0])

                    if result_code != 0:
                        self.logger.error(
                            'A problem occurred while running take screenshot command with default display')
                        self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                     message='Ekran görüntüsü alırken hata oluştu: Komut başarıyla çalıştırılamadı.')
                        return

                else:
                    self.logger.warning('User decline to take screenshot.')
                    self.context.create_response(code=self.message_code.TASK_WARNING.value,
                                                 message='Eklenti başarıyla çalıştı; fakat kullanıcı ekran görüntüsü alınmasına izin vermedi.')
                    return

            else:
                user_display = self.Sessions.display(user_name)
                if not user_display:
                    user_display = '0'

                ##permission
                self.logger.debug(
                    'Asking for screenshot to user {0} on {1} display'.format(user_name, user_display))

                user_answer = self.ask_permission(user_display, user_name,
                                                  "Ekran görüntüsünün alınmasına izin veriyor musunuz?",
                                                  "Ekran Görüntüsü")

                if user_answer is None:
                    self.logger.error('User answer could not kept.')
                    self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                                 message='Ekran görüntüsü alırken hata oluştu: Kullanıcı iznine erişilemedi.')
                    return

                elif user_answer is True:
                    self.logger.debug('User accepted for screenshot')
                    self.logger.debug('Taking screenshot with specified display: {0}'.format(user_display))

                    self.execute(self.take_screenshot.format(user_display.replace(':', '')), as_user=user_name)

                    self.logger.debug('Screenshot command executed.')
                else:
                    self.logger.warning('User decline to take screenshot.')
                    self.context.create_response(code=self.message_code.TASK_WARNING.value,
                                                 message='Eklenti başarıyla çalıştı; fakat kullanıcı ekran görüntüsü alınmasına izin vermedi.')
                    return
                    ##permission###

            if self.is_exist(self.shot_path):
                self.logger.debug('Screenshot file found.')

                data = {}
                md5sum = self.get_md5_file(str(self.shot_path))
                self.logger.debug('{0} renaming to {1}'.format(self.temp_file_name, md5sum))
                self.rename_file(self.shot_path, self.Ahenk.received_dir_path() + md5sum)
                self.logger.debug('Renamed.')
                data['md5'] = md5sum
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Ekran görüntüsü başarıyla alındı.',
                                             data=json.dumps(data),
                                             content_type=self.get_content_type().IMAGE_JPEG.value)
                self.logger.debug('SCREENSHOT task is handled successfully')
            else:
                raise Exception('Image not found this path: {0}'.format(self.shot_path))

        except Exception as e:
            self.logger.error(
                'A problem occured while handling SCREENSHOT task: {0}'.format(traceback.format_exc()))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Ekran görüntüsü alırken hata oluştu: {0}'.format(str(e)))

    def get_username_display(self):
        result_code, p_out, p_err = self.execute("who | awk '{print $1, $5}' | sed 's/(://' | sed 's/)//'", result=True)

        if result_code != 0:
            return None
        lines = str(p_out).split('\n')
        for line in lines:
            arr = line.split(' ')
            if len(arr) > 1 and str(arr[1]).isnumeric() is True and arr[0] != 'root':
                return arr
        return None


def handle_task(task, context):
    screenshot = TakeScreenshot(task, context)
    screenshot.handle_task()
