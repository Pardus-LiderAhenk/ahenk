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
        self.username = self.get_username()
        if self.username is None:
            self.username = self.get_active_user()

    def handle_safe_mode(self):
        profil_full_path = self.local_settings_path+self.local_settings_path_suffix+self.user_js_file
        if self.is_exist(profil_full_path):
            self.delete_file(profil_full_path)
        else:
            self.logger.debug("{0} user's privilege file not found".format(self.username))
        self.default_proxy_settings()

    def default_proxy_settings(self):
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy autoconfig-url '''".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy ignore-hosts ['localhost', '127.0.0.0/8']".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy mode 'none''".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy use-same-proxy true'".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.ftp host '''".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.ftp port 0'".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http host '''".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http port 8080'".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.https host '''".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.https port 0'".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.socks host '''".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.socks port 0'".format(self.username))
        self.execute("su - {0} -c  'gsettings set org.gnome.system.proxy.http use-authentication false'".format(self.username))

def handle_mode(context):
    init = Safe(context)
    init.handle_safe_mode()
