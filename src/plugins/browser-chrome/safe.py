from base.plugin.abstract_plugin import AbstractPlugin


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.logger = self.get_logger()
        self.local_settings_path_suffix = 'policies/managed/'
        self.local_settings_path = '/etc/opt/chrome/'
        self.local_settings_proxy_profile = '/etc/profile.d/'
        self.local_settings_proxy_file = 'liderahenk_chrome_proxy.sh'
        self.user_js_file = 'liderahenk_browser_chrome_preferences.json'
        self.logger.info('Parameters were initialized.')

    def handle_safe_mode(self):

        profil_full_path = self.local_settings_path+self.local_settings_path_suffix+self.user_js_file
        profil_proxy_path = self.local_settings_proxy_profile+self.local_settings_proxy_file

        if self.is_exist(profil_full_path):
            self.delete_file(profil_full_path)
        if self.is_exist(profil_proxy_path):
            self.delete_file(profil_proxy_path)
        else:
            self.logger.debug("{0} user's privilege file not found".format(username))

def handle_mode(context):
    init = Safe(context)
    init.handle_safe_mode()
