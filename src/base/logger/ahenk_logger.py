#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import logging
import logging.config
from inspect import getframeinfo, stack
import sys

from base.scope import Scope


class Logger(object):
    """Ahenk Logger Service
    This module is Ahenk logger service implementation.
    Instance is stored in Scope. Service adds name of script which use logger, with line number.

    Example usage:
        logger = Scope.getInstance().get_logger()
        logger.debug('<debug_message>')
        logger.info('<info_message>')
        logger.warning('<warning_message>')

        logger.error('<error_message>')

    """

    def __init__(self):
        super(Logger, self).__init__()
        scope = Scope.get_instance()
        config_manger = scope.get_configuration_manager()

        logging.config.fileConfig(config_manger.get('BASE', 'logConfigurationFilePath'))
        self.logger = logging.getLogger()

    def get_logger(self):
        return self.logger

    def debug(self, message):
        caller = getframeinfo(stack()[1][0])
        self.logger.debug('[{0} {1}]\t {2}'.format(self.get_log_header(caller.filename), caller.lineno, message))

    def info(self, message):
        caller = getframeinfo(stack()[1][0])
        self.logger.info('[{0} {1}]\t {2}'.format(self.get_log_header(caller.filename), caller.lineno, message))

    def warning(self, message):
        caller = getframeinfo(stack()[1][0])
        self.logger.warning('[{0} {1}]\t {2}'.format(self.get_log_header(caller.filename), caller.lineno, message))

    def error(self, message):
        try:
            exc_type, exc_value, exc_trace_back = sys.exc_info()
            caller = getframeinfo(stack()[1][0])

            if exc_type is None and exc_value is None and exc_trace_back is None:
                self.logger.error('[{0} {1}]\t {2}'.format(self.get_log_header(caller.filename), caller.lineno, message))
            else:
                self.logger.error(
                    '[{0} {1} {2}]\t {3}'.format(self.get_log_header(caller.filename), exc_trace_back.tb_lineno, exc_type,
                                               message))
        except Exception as e:
            self.logger.error(message)

    @staticmethod
    def get_log_header(file_path):

        if file_path is not None:
            name_list = file_path.split('/')
            result = ''
            if len(name_list) > 1:
                result = str(name_list[len(name_list) - 2]).upper() + ' >> ' + name_list[len(name_list) - 1]

            return result
        else:
            return None
