from base.plugin.abstract_plugin import AbstractPlugin


class Safe(AbstractPlugin):
    def __init__(self, context):
        super(Safe, self).__init__()
        self.context = context
        self.username = str(context.get_username())
        self.logger = self.get_logger()
        self.sudoer_file_path = '/etc/sudoers.d/{0}_sudoers'
        self.logger.debug('Parameters were initialized.')

    def handle_safe_mode(self):
        username = self.context.get('username')
        if self.is_exist(self.sudoer_file_path.format(username)):
            self.delete_file(self.sudoer_file_path.format(username))
            self.logger.debug('User sudoers removed privilege from {0}.'.format(username))

        else:
            self.logger.debug("{0} user's privilege file not found".format(username))

def handle_mode(context):
    init = Safe(context)
    init.handle_safe_mode()
