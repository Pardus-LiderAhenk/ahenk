#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tuncay ÇOLAK <tuncay.colak@tubitak.gov.tr>

import os
import importlib.util
from base.plugin.abstract_plugin import AbstractPlugin
from base.model.enum.desktop_type import DesktopType
from base.util.display_helper import DisplayServerType

def load_module_from_file(file_path, module_name):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def handle_task(task, context):

    temp_instance = AbstractPlugin()
    logger = temp_instance.get_logger()
    
    try:
        desktop_env = temp_instance.get_desktop_env()
        logger.info(f'Detected desktop environment: {desktop_env}')
        
        current_dir = os.path.dirname(os.path.abspath(__file__))

        if desktop_env.lower() == DesktopType.GNOME.name.lower() and DisplayServerType.detect_desktop_env() == DisplayServerType.WAYLAND.value:
            logger.info('Routing to GNOME Remote Desktop setup...')
            gnome_module_path = os.path.join(current_dir, 'rdp_remote_desktop.py')
            gnome_module = load_module_from_file(gnome_module_path, 'rdp_remote_desktop')
            gnome_module.handle_task(task, context)
            
        elif desktop_env == DesktopType.GNOME.name.lower() and DisplayServerType.detect_desktop_env() == DisplayServerType.X11.value:
            logger.info('Routing to GNOME VNC server setup...')
            gnome_module_path = os.path.join(current_dir, 'vnc_remote_desktop.py')
            gnome_module = load_module_from_file(gnome_module_path, 'vnc_remote_desktop')
            gnome_module.handle_task(task, context)
            
        elif desktop_env == DesktopType.XFCE.name.lower():
            logger.info('Routing to XFCE VNC server setup...')
            xfce_module_path = os.path.join(current_dir, 'vnc_remote_desktop.py')
            xfce_module = load_module_from_file(xfce_module_path, 'vnc_remote_desktop')
            xfce_module.handle_task(task, context)
            
        else:
            logger.warning(f'Unsupported desktop environment: {desktop_env}')
            context.create_response(
                code=temp_instance.get_message_code().TASK_ERROR.value,
                message=f'Desteklenmeyen masaüstü ortamı: {desktop_env}',
            )
            
    except Exception as e:
        logger.error(f'Error in setup router: {str(e)}')
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            xfce_module_path = os.path.join(current_dir, 'vnc_remote_desktop.py')
            xfce_module = load_module_from_file(xfce_module_path, 'vnc_remote_desktop')
            xfce_module.handle_task(task, context)
        except Exception as fallback_error:
            logger.error(f'Fallback handler also failed: {str(fallback_error)}')
            context.create_response(
                code=temp_instance.get_message_code().TASK_ERROR.value,
                message=f'Uzak masaüstü yapılandırılırken hata oluştu: {str(e)}'
            )

