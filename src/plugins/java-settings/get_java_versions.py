#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json, re
from base.plugin.abstract_plugin import AbstractPlugin

class GetJavaVersions(AbstractPlugin):
    def __init__(self, task, context):
        super(AbstractPlugin, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            java_versions = self._get_available_java_versions()
            if java_versions is None:
                return
            
            default_version = self._get_default_java_version()
            if default_version is None:
                return
            
            self._send_success_response(java_versions, default_version)
            
        except Exception as e:
            self.logger.error(f'Exception in get_java_versions: {str(e)}')
            self._send_error_response(f'Java versiyonları alınırken hata oluştu: {str(e)}')

    def _get_available_java_versions(self):
        result_code, stdout, stderr = self.execute('/usr/sbin/update-java-alternatives -l')
        
        if result_code != 0:
            self.logger.error(f'Error executing command: {stderr}')
            self._send_error_response('Java versiyonları alınırken hata oluştu.', {'error': str(stderr)})
            return None
        
        java_versions = []
        for line in stdout.strip().split('\n'):
            if not line.strip():
                continue
                
            parts = line.split()
            if len(parts) < 3:
                self.logger.warning(f'Skipping malformed line: {line}')
                continue
                
            java_versions.append({
                'name': parts[0],
                'label': self._parse_java_name(parts[0])
            })
        
        return java_versions


    def _get_default_java_version(self):
        result_code, stdout, stderr = self.execute('readlink -f $(which java)')
        
        if result_code != 0:
            self.logger.error(f'Error executing command: {stderr}')
            self._send_error_response('Default Java versiyonu alınırken hata oluştu.', {'error': str(stderr)})
            return None
        
        return self._path_to_jdk(stdout.strip())

    def _send_error_response(self, message, data=None):
        self.context.create_response(
            code=self.message_code.TASK_ERROR.value,
            message=message,
            content_type=self.get_content_type().APPLICATION_JSON.value,
            data=json.dumps(data) if data else None
        )

    def _send_success_response(self, java_versions, default_version):
        self.logger.debug(f'Found {len(java_versions)} Java versions + Default version: {default_version}')
        self.context.create_response(
            code=self.message_code.TASK_PROCESSED.value,
            content_type=self.get_content_type().APPLICATION_JSON.value,
            message='JDKlar listelendi.',
            data=json.dumps({
                'javaVersions': java_versions,
                'defaultVersion': default_version
            })
        )

    def _parse_java_name(self, raw_name):
        if "oracle" in raw_name.lower():
            vendor = "Oracle Java" if "java" in raw_name.lower() else "Oracle JDK"
        elif "openjdk" in raw_name.lower():
            vendor = "OpenJDK"
        else:
            return "Unknown Java"

        version_match = re.search(r'(\d+(\.\d+)*)', raw_name)

        if version_match:
            version_str = version_match.group(1)
            if version_str.startswith("1."):
                version = version_str.split(".")[1]
            else:
                version = version_str.split(".")[0]
        else:
            version = "Unknown Version"

        return f"{vendor} {version}"
    
    def _path_to_jdk(self, java_path):
        try:
            match = re.search(r'/jvm/([^/]+)', java_path)
            if not match:
                return None
            
            folder_name = match.group(1)
            
            if folder_name.startswith("java-1."):
                return folder_name

            if folder_name.startswith("java-"):
                version_match = re.match(r'java-(\d+)(.*)', folder_name)
                if version_match:
                    version = version_match.group(1)
                    rest = version_match.group(2).strip("-")
                    return f'java-1.{version}.0-{rest}'
                
            return folder_name

        except Exception as e:
            self.logger.error(f"Path parsing error: {e}")
            return None
    

def handle_task(task, context):
    plugin = GetJavaVersions(task, context)
    plugin.handle_task()