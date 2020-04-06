#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:Mine DOGAN <mine.dogan@agem.com.tr>

import json
import os
import sys

from base.plugin.abstract_plugin import AbstractPlugin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fstab import Fstab
from api.disk_quota import DiskQuota

def handle_policy(profile_data, context):
    dq = DiskQuota(profile_data, context)
    dq.handle_policy()
