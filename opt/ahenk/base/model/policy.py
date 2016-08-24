#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: İsmail BAŞARAN <ismail.basaran@tubitak.gov.tr> <basaran.ismaill@gmail.com>
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>
import json

from base.model.profile import Profile


class Policy(object):
    """docstring for Policy"""

    def __init__(self, message):
        self.policy = message

    @property
    def ahenk_policy_version(self):
        return self.policy['agentPolicyVersion']

    @property
    def ahenk_profiles(self):
        profiles = []
        for p in self.policy['agentPolicyProfiles']:
            profiles.append(Profile(p))
        return profiles

    @property
    def user_policy_version(self):
        return self.policy['userPolicyVersion']

    @property
    def timestamp(self):
        return self.policy['timestamp']

    @property
    def user_profiles(self):
        profiles = []
        try:
            for p in self.policy['userPolicyProfiles']:
                profiles.append(Profile(p))
            return profiles
        except Exception as e:
            return None

    @property
    def username(self):
        return self.policy['username']

    # TODO result mesajı dönerken döndür
    @property
    def ahenk_execution_id(self):
        return self.policy['agentCommandExecutionId']

    @property
    def user_execution_id(self):
        return self.policy['userCommandExecutionId']

    def to_string(self):
        return str(self.policy)

    def to_json(self):
        return json.load(self.policy)

    def obj_name(self):
        return "PROFILE"
