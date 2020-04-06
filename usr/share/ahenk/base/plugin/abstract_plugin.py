#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.scope import Scope
from base.model.enum.content_type import ContentType
from base.model.enum.message_code import MessageCode
from base.system.system import System
from base.util.util import Util


class AbstractPlugin(Util, System):
    """This is base class for plugins"""

    def __init__(self):
        super(AbstractPlugin, self).__init__()
        self.scope = Scope.get_instance()

    def handle_task(profile_data, context):
        Scope.get_instance().get_logger().error('Handle function not found')

    def get_message_code(self):
        return MessageCode

    def get_content_type(self):
        return ContentType

    def get_logger(self):
        try:
            return Scope.get_instance().get_logger()
        except Exception as e:
            self.scope.get_logger().error(
                'A problem occurred while getting logger. Error Message: {0}'.format(str(e)))
            return None


def configuration_manager(self):
    try:
        return self.scope.get_configuration_manager()
    except Exception as e:
        self.logger().error(
            'A problem occurred while getting configuration manager. Error Message: {0}'.format(
                str(e)))
        return None


def plugin_path(self):
    return self.configuration_manager().get('PLUGIN', 'pluginfolderpath')
