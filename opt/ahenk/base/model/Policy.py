#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
from base.model.Profile import Profile
import json

class Policy(object):
    """docstring for Policy"""
    def __init__(self,message):
        self.policy = message

    @property
    def ahenk_policy_version(self):
        return self.policy['ahenkpolicyversion']

    @property
    def ahenk_profiles(self):
        profiles=[]
        for p in self.policy['ahenkprofiles']:
            profiles.append(Profile(p))
        return profiles

    @property
    def user_policy_version(self):
        return self.policy['userpolicyversion']

    @property
    def timestamp(self):
        self.request['timestamp']

    @property
    def user_profiles(self):
        profiles=[]
        for p in self.policy['userprofiles']:
            profiles.append(Profile(p))
        return profiles

    def to_string(self):
        return str(self.policy)

    def to_json(self):
        return json.load(self.policy)
