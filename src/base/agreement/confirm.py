#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base.util.display_helper import DisplayHelper, DisplayServerType
from base.util.util import Util
from base.scope import Scope


def show_message(message, title="Liderahenk Bildiri"):
    try:
        session = DisplayServerType.detect_desktop_env()
        user = Util.get_active_local_user()

        display = DisplayHelper.detect_user_display(user)
        if user is None or display is None:
            Scope.get_instance().get_logger().debug(
                f"No display found for user={user}"
            )
            return "no_display"

        env_string = DisplayHelper.build_env_string(
            desktop_server_type=session,
            user=user
        )

        command = (
            f"su {user} -c \"{env_string} "
            f"zenity --info --width=400 --height=200 "
            f"--title '{title}' --text '{message}'\""
        )

        result_code, _, _ = Util.execute(command)

        if result_code != 0:
            return "error"
        
        return "success"

    except Exception as e:
        Scope.get_instance().get_logger().error(
            f"Error while showing zenity message: {e}"
        )
        return "error"
