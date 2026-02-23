#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum


class DesktopType(Enum):
    GNOME = '/usr/bin/gnome-session'
    XFCE = '/usr/bin/xfce4-session'
    CINNAMON = '/usr/bin/cinnamon-session'

    @classmethod
    def as_list(cls):
        return [member.value for member in cls]

    @classmethod
    def names_as_list(cls):
        return [member.name for member in cls]


class DisplayManagerUser(Enum):
    """
    Linux Display Manager 
    """

    GDM = "gdm"
    LIGHTDM = "lightdm"
    KDM = "kdm"
    DEBIANGDM = "Debian-gdm"

    @classmethod
    def as_list(cls):
        return [member.value for member in cls]

    @classmethod
    def names_as_list(cls):
        return [member.name for member in cls]
    
    @classmethod
    def all_users(cls):
        return [member.value for member in cls]

    @classmethod
    def get_user(cls, dm_name: str):
        """
        örn: get_user("lightdm") → "lightdm"
        """
        key = dm_name.upper()
        if key in cls.__members__:
            return cls[key].value
        return None
