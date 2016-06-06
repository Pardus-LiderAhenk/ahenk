#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.Scope import Scope
from base.model.enum.ContentType import ContentType
from base.model.enum.MessageCode import MessageCode
from base.system.system import System
from base.util.util import Util


class AbstractPlugin(Util, System):
    """This is base class for plugins"""

    def __init__(self):
        super(AbstractPlugin, self).__init__()
        self.scope = Scope.getInstance()

    def handle_task(profile_data, context):
        Scope.getInstance().getLogger().error('[AbstractPlugin] Handle function not found')

    def get_message_code(self):
        return MessageCode

    def get_content_type(self):
        return ContentType

    def get_logger(self):
        try:
            return Scope.getInstance().getLogger()
        except Exception as e:
            self.scope.getLogger().error('[AbstractPlugin] A problem occurred while getting logger. Error Message: {}'.format(str(e)))
            return None


def configuration_manager(self):
    try:
        return self.scope.getConfigurationManager()
    except Exception as e:
        self.logger().error('[AbstractPlugin] A problem occurred while getting configuration manager. Error Message: {}'.format(str(e)))
        return None


def plugin_path(self):
    return self.configuration_manager().get('PLUGIN', 'pluginfolderpath')
