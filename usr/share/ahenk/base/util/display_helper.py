#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import psutil
from base.util.util import Util
from enum import Enum
import pwd
import glob
from base.model.enum.desktop_type import DesktopType
from base.system.system import System



class DisplayHelper:

    @staticmethod
    def get_user_session(user):
        """
        get session ID from systemd
        """
        out = subprocess.check_output(
            ["loginctl", "list-sessions"],
            text=True
        ).strip().split("\n")

        for line in out[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == user:
                return parts[0]  # Session ID
        return None

    @staticmethod
    def get_loginctl_env(session_id, var):
        """
        get env variable in loginctl
        """
        try:
            out = subprocess.check_output(
                ["loginctl", "show-session", session_id, f"-p{var}"],
                text=True
            ).strip()

            if "=" in out:
                return out.split("=", 1)[1]
        except Exception:
            return None
        return None

    @staticmethod
    def get_socket_wayland_display(user):
        """
        /run/user/<uid>/wayland-* socket WAYLAND_DISPLAY.
        """
        try:
            uid = pwd.getpwnam(user).pw_uid
            sockets = glob.glob(f"/run/user/{uid}/wayland-*")
            if not sockets:
                return None

            # /run/user/1000/wayland-0 → wayland-0
            return sockets[0].split("/")[-1]
        except Exception:
            return None

    @staticmethod
    def get_wayland_env(user):
        env = {}

        session = DisplayHelper.get_user_session(user)

        if session:
            env['WAYLAND_DISPLAY'] = DisplayHelper.get_loginctl_env(session, "WAYLAND_DISPLAY")
            env['XDG_RUNTIME_DIR'] = DisplayHelper.get_loginctl_env(session, "XDG_RUNTIME_DIR")
            env['DBUS_SESSION_BUS_ADDRESS'] = DisplayHelper.get_loginctl_env(session, "DBUS_SESSION_BUS_ADDRESS")

        if not env.get("WAYLAND_DISPLAY"):
            env['WAYLAND_DISPLAY'] = DisplayHelper.get_socket_wayland_display(user)

        if not env.get("XDG_RUNTIME_DIR"):
            uid = pwd.getpwnam(user).pw_uid
            env['XDG_RUNTIME_DIR'] = f"/run/user/{uid}"

        if not env.get("DBUS_SESSION_BUS_ADDRESS"):
            uid = pwd.getpwnam(user).pw_uid
            env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{uid}/bus"

        return env


    @staticmethod
    def get_x11_env(user):
        """
        get x11 env by user
        """
        env = {}
        desktop_env = Util.get_desktop_env()
        try:
            env['DISPLAY'] = DisplayHelper.detect_user_display(user)
        except Exception:
            return None

        return env

    @staticmethod
    def build_env_string(desktop_server_type=None, user=None):
        """
        {key: value} -> 'KEY=value KEY2=value2'
        """
        if desktop_server_type == "wayland":
            env_dict = DisplayHelper.get_wayland_env(user)
        else:
            env_dict = DisplayHelper.get_x11_env(user)

        if not env_dict:
            return ""
        parts = []
        for k, v in env_dict.items():
            if v:
                parts.append(f'{k}={v}')
        return " ".join(parts)
    
    @staticmethod
    def get_username_display():
        result_code, p_out, p_err = Util.execute("who | awk '{print $1, $5}' | sed 's/(://' | sed 's/)//'", result=True)
        result = []
        display_number = None
        lines = str(p_out).split('\n')
        for line in lines:
            arr = line.split(' ')
            if len(arr) > 1 and str(arr[1]).isnumeric() is True:
                result.append(line)

        params = str(result[0]).split(' ')
        display_number = params[1]
        display_number = ":"+str(display_number)
        return display_number

    @staticmethod
    def get_username_display_gnome(user):
        result_code, p_out, p_err = Util.execute("who | awk '{print $1, $5}' | sed 's/(://' | sed 's/)//'", result=True)
        display_number = None
        result = []
        lines = str(p_out).split('\n')
        for line in lines:
            arr = line.split(' ')
            if len(arr) > 1 and str(arr[1]).isnumeric() is True:
                result.append(line)
        for res in result:
            arr = res.split(" ")
            username = arr[0]
            if username == user:
                display_number = ":" + arr[1]
        return display_number
    


    @staticmethod
    def detect_user_display(user=None):
        if DisplayServerType.detect_desktop_env() is DisplayServerType.WAYLAND.value:
            return DisplayHelper.get_socket_wayland_display(user)

        if DisplayServerType.detect_desktop_env() is DisplayServerType.X11.value:
            desktop_env = Util.get_desktop_env()
            if desktop_env == "gnome":
                gnome_display = DisplayHelper.get_username_display_gnome(user)
                if gnome_display is None:
                    return DisplayHelper.detect_display_socket_base(user)
                return gnome_display
            if desktop_env == "xfce":
                # return System.Sessions.display(user)
                return DisplayHelper.get_username_display()
        return None
    
    
    """
    X11 UNIX domain socket ownership based DISPLAY detection
    """
    @staticmethod
    def detect_display_socket_base(username):
        uid = pwd.getpwnam(username).pw_uid
        base = "/tmp/.X11-unix"

        if not os.path.isdir(base):
            return None

        for entry in os.listdir(base):
            if not entry.startswith("X"):
                continue

            path = os.path.join(base, entry)
            st = os.stat(path)

            if st.st_uid == uid:
                return f":{entry[1:]}"

        return None
    
    
class DisplayServerType(Enum):
    X11 = 'x11'
    WAYLAND = 'wayland'

    @classmethod
    def as_list(cls):
        return [member.value for member in cls]

    @classmethod
    def names_as_list(cls):
        return [member.name for member in cls]

    @classmethod
    def detect(cls):
        """
        1) XDG_SESSION_TYPE
        2) Xwayland / Xorg
        3) None fallback
        """
        t = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if t == "wayland":
            return cls.WAYLAND
        if t == "x11":
            return cls.X11

        try:
            for p in psutil.process_iter(['name']):
                name = p.info['name']
                if name == 'Xwayland':
                    return cls.WAYLAND
                if name == 'Xorg':
                    return cls.X11
        except Exception:
            pass

        return None

    @classmethod
    def detect_desktop_env(cls):
        """
        return 'x11', 'wayland' or None (value)
        """
        display = cls.detect()

        if display is None:
            return None

        return display.value

