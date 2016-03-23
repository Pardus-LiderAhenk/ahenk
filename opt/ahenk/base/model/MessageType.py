#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
from enum import Enum


class MessageType(Enum):
    TASK_RECEIVED = 'TASK_RECEIVED'
    TASK_PROCESSING = 'TASK_PROCESSING'
    TASK_PROCESSED = 'TASK_PROCESSED'
    TASK_ERROR = 'TASK_ERROR'
    TASK_WARNING = 'TASK_WARNING'
    POLICY_RECEIVED = 'POLICY_RECEIVED'
    POLICY_PROCESSED = 'POLICY_PROCESSED'
