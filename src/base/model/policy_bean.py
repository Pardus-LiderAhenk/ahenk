#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>


class PolicyBean(object):
    """docstring for PolicyBean"""

    def __init__(self, policy_id=None, ahenk_policy_version=None, user_policy_version=None, ahenk_profiles=None, user_profiles=None,
                 timestamp=None, username=None, agent_execution_id=None, user_execution_id=None,
                 agent_expiration_date=None, user_expiration_date=None, is_deleted=None, assign_date=None):
        self.policy_id = policy_id
        self.ahenk_policy_version = ahenk_policy_version
        self.user_policy_version = user_policy_version
        self.ahenk_profiles = ahenk_profiles
        self.user_profiles = user_profiles
        self.timestamp = timestamp
        self.username = username
        self.agent_execution_id = agent_execution_id
        self.user_execution_id = user_execution_id
        self.agent_expiration_date = agent_expiration_date
        self.user_expiration_date = user_expiration_date
        self.is_deleted = is_deleted
        self.assign_date = assign_date

    def get_policy_id(self):
        return self.policy_id

    def set_policy_id(self, policy_id):
        self.policy_id = policy_id

    def get_ahenk_policy_version(self):
        return self.ahenk_policy_version

    def set_ahenk_policy_version(self, ahenk_policy_version):
        self.ahenk_policy_version = ahenk_policy_version

    def get_user_policy_version(self):
        return self.user_policy_version

    def set_user_policy_version(self, user_policy_version):
        self.user_policy_version = user_policy_version

    def get_ahenk_profiles(self):
        return self.ahenk_profiles

    def set_ahenk_profiles(self, ahenk_profiles):
        self.ahenk_profiles = ahenk_profiles

    def get_user_profiles(self):
        return self.user_profiles

    def set_user_profiles(self, user_profiles):
        self.user_profiles = user_profiles

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_agent_execution_id(self):
        return self.agent_execution_id

    def set_agent_execution_id(self, agent_execution_id):
        self.agent_execution_id = agent_execution_id

    def set_user_execution_id(self, user_execution_id):
        self.user_execution_id = user_execution_id

    def get_user_execution_id(self):
        return self.user_execution_id

    def set_is_deleted(self, is_deleted):
        self.is_deleted = is_deleted

    def get_is_deleted(self):
        return self.is_deleted

    def set_assign_date(self, assign_date):
        self.assign_date = assign_date

    def get_assign_date(self):
        return self.assign_date