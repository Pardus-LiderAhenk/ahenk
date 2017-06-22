from base.plugin.abstract_plugin import AbstractPlugin


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.username = str(context.get_username())
        self.logger = self.get_logger()
        self.sudoer_line = '{0} ALL = NOPASSWD : /usr/bin/apt-get , /usr/bin/aptitude'
        self.sudoer_file_path = '/etc/sudoers'
        self.logger.debug('Parameters were initialized.')

    def handle_safe_mode(self):
        sudoer_data = self.read_file(self.sudoer_file_path)
        self.write_file(self.sudoer_file_path, sudoer_data.replace(self.sudoer_line.format(self.username), ''))
        self.logger.debug('User sudoers removed privilege from {0}.'.format(self.username))


def handle_mode(context):
    init = Safe(context)
    init.handle_safe_mode()
