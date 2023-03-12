from base.plugin.abstract_plugin import AbstractPlugin


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.logger = self.get_logger()
        self.local_settings_path_suffix = 'policies/managed/'
        self.local_settings_path = '/etc/opt/chrome/'
        self.user_js_file = 'liderahenk_browser_chrome_preferences.json'
        self.logger.info('Parameters were initialized.')
        self.username = self.context.get('username')

    def handle_safe_mode(self):
        profil_full_path = self.local_settings_path+self.local_settings_path_suffix+self.user_js_file
        if self.is_exist(profil_full_path):
            self.delete_file(profil_full_path)
        else:
            self.logger.debug("{0} user's privilege file not found".format(self.username))
        self.default_proxy_settings()

    def default_proxy_settings(self):
        if (self.execute("su - {0} -c  'gsettings get org.gnome.system.proxy mode'".format(self.username))) != "'none'":
            self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy mode 'none''".format(self.username))

def handle_mode(context):
    init = Safe(context)
    init.handle_safe_mode()
