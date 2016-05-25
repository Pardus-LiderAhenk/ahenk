#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.Scope import Scope
from base.util.util import Util
from base.model.enum.MessageCode import MessageCode


class AbstractPlugin(Util):
    """This is base class for plugins"""

    def __init__(self):
        super(Util, self).__init__()
        self.scope = Scope.getInstance()
        self.message_code = MessageCode

    def handle_task(profile_data, context):
        Scope.getInstance().getLogger().error('[PluginPolicy] Handle function not found')

    @property
    def logger(self):
        try:
            return self.scope.getLogger()
        except Exception as e:
            self.scope.getLogger().error('[PluginPolicy] A problem occurred while getting logger. Error Message: {}'.format(str(e)))
            return None

    def configuration_manager(self):
        try:
            return self.scope.getConfigurationManager()
        except Exception as e:
            self.logger().error('[PluginPolicy] A problem occurred while getting configuration manager. Error Message: {}'.format(str(e)))
            return None

    def plugin_path(self):
        return self.configuration_manager().get('PLUGIN', 'pluginfolderpath')

