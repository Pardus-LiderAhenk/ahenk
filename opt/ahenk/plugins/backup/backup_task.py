#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Seren Piri <seren.piri@agem.com.tr>

import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backup_util import BackupUtil

def handle_task(task, context):
    backup = BackupUtil(task, context, 'task')
    backup.backup()