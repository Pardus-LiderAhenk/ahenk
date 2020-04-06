#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Caner Feyzullahoglu <caner.feyzullahoglu@agem.com.tr>
"""
Style Guide is PEP-8
https://www.python.org/dev/peps/pep-0008/
"""
import json
import os

from base.plugin.abstract_plugin import AbstractPlugin


class UserPrivilege(AbstractPlugin):
    def __init__(self, profile_data, context):
        super(AbstractPlugin, self).__init__()
        self.profile_data = profile_data
        self.context = context
        self.logger = self.get_logger()

        # self.logger = self.context.logger

        self.polkit_action_folder_path = '/usr/share/polkit-1/actions/'
        self.polkit_pkla_folder_path = '/etc/polkit-1/localauthority/50-local.d/'
        self.default_action_pref = 'tr.org.pardus.mys.pkexec.'

        # self.permission_file_path = self.agent_config.get("UserPolicyPlugin", "userpolicyplugin.policyfile")
        # The below line was like above line at old version.
        self.permission_file_path = '/etc/ahenk/userpolicies'
        # "permission_file"_path was being taken from a config file which has been created by "agentconfig.py"
        # but this py is not present in new version. So I created it as a static string.

    def limit_ahenk(self, item):

        if self.has_attr_json(item, 'cpu') and item['cpu'] is not None and item['cpu'] is not '':
            self.logger.debug('Limiting ahenk cpu usage. Cpu limit value: {0}'.format(item['cpu']))
            self.execute('cpulimit -p {0} -l {1} -z &'.format(str(self.Ahenk.get_pid_number()), str(item['cpu'])),
                         result=False)
            self.logger.debug('Limited ahenk cpu usage. Cpu limit value: {0}'.format(item['cpu']))

    def handle_policy(self):
        print('Handling policy')
        self.logger.debug('Handling policy.')
        # Get username.
        # It is actually user UID in LDAP. The message being created in PolicySubscriberImpl by using
        # MessageFactoryImpl at server side.
        # At agent side Plugin.py takes a message from queue as an item, finds related plugin module by using
        # Scope (with parameters from the item such as plugin name and plugin version), puts "username" to context and
        # triggers "handle_policy" method of related plugin.
        username = self.context.get('username')

        try:
            result_message = ''

            if username is not None:
                self.logger.debug('Getting profile data.')
                data = json.loads(self.profile_data)
                privilege_items = data['items']

                # Lists that will keep user names for cleaning on logout
                add_user_list = list()
                del_user_list = list()
                # List that will keep command paths
                command_path_list = list()

                if len(privilege_items) > 0:
                    self.logger.debug('Iterating over privilege items.')

                    for item in privilege_items:
                        command_path = item['cmd'].strip()
                        if command_path == "/opt/ahenk/ahenkd":
                            self.limit_ahenk(item)
                            continue

                        if self.is_exist(command_path) is False:
                            self.logger.warning(
                                '{0} command path not found. User privilege execution will not processed for this command.'.format(
                                    command_path))
                            continue

                        polkit_status = item['polkitStatus']

                        # Create polkit for each item
                        if polkit_status == 'privileged':

                            self.logger.debug('Parsing command.')
                            command = str(self.parse_command(command_path))

                            action_id = self.default_action_pref + command

                            if not os.path.exists(action_id + '.policy'):
                                self.logger.debug(
                                    'Creating action; command: ' + command + ', action_id: ' + action_id +
                                    ', command_path: ' + command_path)
                                self.create_action(command, action_id, command_path)

                            self.logger.debug(
                                'Executing: "getent group ' + command + ' || groupadd ' + command + '"')
                            self.execute('getent group ' + command + ' || groupadd ' + command)

                            self.logger.debug(
                                'Executing: "adduser ' + str(username) + ' ' + command + '"')
                            self.execute('adduser ' + str(username) + ' ' + command)

                            self.logger.debug('Adding command to add_user_list')
                            add_user_list.append(command)

                            if not os.path.exists(action_id + '.pkla'):
                                self.logger.debug(
                                    'Creating pkla; command: ' + command + ', action_id: ' + action_id)
                                self.create_pkla(command, action_id)

                            self.logger.debug('Executing: "grep "pkexec" ' + str(command_path) + '"')
                            (result_code, p_out, p_err) = self.execute('grep "pkexec" ' + str(command_path))

                            if result_code != 0:
                                # Get resource limit choice
                                limit_resource_usage = item['limitResourceUsage']
                                # Get CPU and memory usage parameters
                                cpu = item['cpu']
                                memory = item['memory']

                                # Create wrapper command with resource limits
                                self.logger.debug(
                                    'Creating wrapper command; command_path: ' + command_path +
                                    ', limit_resource_usage: ' + str(limit_resource_usage) + ', cpu: ' +
                                    str(cpu) + ', memory: ' + str(memory))
                                (wrapper_result, p_out, p_err) = self.create_wrapper_command(command_path,
                                                                                             polkit_status,
                                                                                             limit_resource_usage,
                                                                                             cpu, memory,
                                                                                             command_path_list)

                                if wrapper_result == 0:
                                    self.logger.debug('Wrapper created successfully.')
                                    self.logger.debug('Adding item result to result_message.')
                                    result_message += command_path + ' | Ayrıcalıklı | Başarılı, '
                                else:
                                    self.logger.debug('Adding item result to result_message.')
                                    result_message += command_path + ' | Ayrıcalıklı | Başarısız, '

                        elif polkit_status == 'unprivileged':

                            self.logger.debug('Parsing command.')
                            command = str(self.parse_command(command_path))

                            action_id = self.default_action_pref + command

                            if not os.path.exists(action_id + '.policy'):
                                self.logger.debug(
                                    'Creating action; command: ' + command + ', action_id: ' + action_id +
                                    ', command_path: ' + command_path)
                                self.create_action(command, action_id, command_path)

                            self.logger.debug(
                                'Executing: "getent group ' + command + ' || groupadd ' + command + '"')
                            self.execute('getent group ' + command + ' || groupadd ' + command)

                            self.logger.debug(
                                'Executing: "deluser ' + str(username) + ' ' + command + '"')
                            self.execute('deluser ' + str(username) + ' ' + command)

                            self.logger.debug('Adding command to del_user_list')
                            del_user_list.append(command)

                            if not os.path.exists(action_id + '.pkla'):
                                self.logger.debug(
                                    'Creating pkla; command: ' + command + ', action_id: ' + action_id)
                                self.create_pkla(command, action_id)

                            self.logger.debug('Executing: "grep "pkexec" ' + str(command_path) + '"')
                            (result_code, p_out, p_err) = self.execute('grep "pkexec" ' + str(command_path))

                            if result_code != 0:
                                # Get resource limit choice
                                limit_resource_usage = item['limitResourceUsage']
                                # Get CPU and memory usage parameters
                                cpu = item['cpu']
                                memory = item['memory']

                                # Create wrapper command with resource limits
                                self.logger.debug(
                                    'Creating wrapper command; command_path: ' + command_path +
                                    ', limit_resource_usage: ' + str(limit_resource_usage) + ', cpu: ' +
                                    str(cpu) + ', memory: ' + str(memory))
                                (wrapper_result, p_out, p_err) = self.create_wrapper_command(command_path,
                                                                                             polkit_status,
                                                                                             limit_resource_usage,
                                                                                             cpu, memory,
                                                                                             command_path_list)
                                if wrapper_result == 0:
                                    self.logger.debug('Wrapper created successfully.')
                                    self.logger.debug('Adding item result to result_message.')
                                    result_message += command_path + ' | Ayrıcalıksız | Başarılı, '
                                else:
                                    self.logger.debug('Adding item result to result_message.')
                                    result_message += command_path + ' | Ayrıcalıksız | Başarısız, '

                        elif polkit_status == 'na':

                            self.logger.debug(
                                'polkit_status is: na, no action or pkla will be created.')

                            # Get resource limit choice
                            limit_resource_usage = item['limitResourceUsage']
                            # Get CPU and memory usage parameters
                            cpu = item['cpu']
                            memory = item['memory']

                            # Create wrapper command with resource limits
                            self.logger.debug(
                                'Creating wrapper command; command_path: ' + command_path +
                                ', limit_resource_usage: ' + str(limit_resource_usage) + ', cpu: ' +
                                str(cpu) + ', memory: ' + str(memory))
                            (wrapper_result, p_out, p_err) = self.create_wrapper_command(command_path, polkit_status,
                                                                                         limit_resource_usage,
                                                                                         cpu, memory, command_path_list)

                            if wrapper_result == 0:
                                self.logger.debug('Wrapper created successfully.')
                                self.logger.debug('Adding item result to result_message.')
                                result_message += command_path + ' | Ayrıcalıklı | Başarılı, '
                            else:
                                self.logger.debug('Adding item result to result_message.')
                                result_message += command_path + ' | Ayrıcalıklı | Başarısız, '

                self.logger.debug('Getting plugin path.')

                p_path = self.Ahenk.plugins_path()

                self.logger.debug('Creating logout files.')
                self.create_logout_files(username, p_path, add_user_list, del_user_list, command_path_list)

                self.logger.debug('Creating response.')
                self.context.create_response(code=self.get_message_code().POLICY_PROCESSED.value,
                                             message=result_message)

                self.logger.debug('User Privilege profile is handled successfully.')

            else:
                self.logger.debug('Creating response.')
                self.context.create_response(code=self.get_message_code().POLICY_WARNING.value,
                                             message='Kullanıcı adı olmadan USER PRIVILEGE profili çalıştırılamaz.')

        except Exception as e:
            self.context.create_response(code=self.get_message_code().POLICY_ERROR.value,
                                         message='USER PRIVILEGE profili uygulanırken bir hata oluştu.')
            self.logger.error(
                'A problem occurred while handling User Privilege profile: {0}'.format(str(e)))

    def parse_command(self, command_path):
        splitted_command_str = str(command_path).split('/')
        return splitted_command_str[-1]

    def create_action(self, command, command_id, command_path):
        command_path += '-ahenk'
        action_str = '<?xml version="1.0" encoding="UTF-8"?> \n' \
                     ' <!DOCTYPE policyconfig PUBLIC \n' \
                     ' "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN" \n' \
                     ' "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd"> \n' \
                     ' <policyconfig> \n' \
                     ' <action id="{action_id}"> \n' \
                     ' <message>Please enter the password for this action</message> \n' \
                     ' <icon_name>{cmd}</icon_name> \n' \
                     ' <defaults> \n' \
                     ' <allow_any>auth_admin</allow_any> \n' \
                     ' <allow_inactive>auth_admin</allow_inactive> \n' \
                     ' <allow_active>auth_admin</allow_active> \n' \
                     ' </defaults> \n' \
                     ' <annotate key="org.freedesktop.policykit.exec.path">{cmd_path}</annotate> \n' \
                     ' <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate> \n' \
                     ' </action>\n' \
                     ' </policyconfig> \n'.format(action_id=command_id, cmd=command, cmd_path=command_path)

        action_file_path = self.polkit_action_folder_path + command_id + '.policy'
        action_file = open(action_file_path, 'w')
        action_file.write(action_str)
        action_file.close()

    def create_pkla(self, command, action_id):
        pkla_str = '[Normal Staff Permissions]\n' \
                   'Identity=unix-group:{grp}\n' \
                   'Action={actionId}\n' \
                   'ResultAny=no\n' \
                   'ResultInactive=no\n' \
                   'ResultActive=yes\n'.format(grp=command, actionId=action_id)

        pkla_file_path = self.polkit_pkla_folder_path + action_id + '.pkla'
        pkla_file = open(pkla_file_path, 'w')
        pkla_file.write(pkla_str)
        pkla_file.close()

    def create_wrapper_command(self, command_path, polkit_status, limit_resource_usage, cpu, memory, command_path_list):
        self.logger.debug(
            'Executing: "' + 'mv ' + str(command_path) + ' ' + str(command_path) + '-ahenk"')
        (result_code, p_out, p_err) = self.execute(
            'mv ' + str(command_path) + ' ' + str(command_path) + '-ahenk')

        if result_code == 0:

            command_path_str = str(command_path).strip()

            line = 'if [ \( "$USER" = "root" \) -o \( "$USER" = "" \) ]; then \n' + str(command_path) + '-ahenk $@'
            if limit_resource_usage:
                line += '\nelse\n'
                line += self.add_resource_limits(command_path, polkit_status, cpu, memory)
            else:
                if polkit_status == 'na':
                    line = line + '\nelse\n' + str(command_path) + '-ahenk $@\n'
                else:
                    line += '\nelse\nCOMMAND=\"' + str(command_path) + '-ahenk $@\"\n'
                    line += 'pkexec --user $USER $COMMAND\n'
            line += 'fi'

            self.logger.debug('Writing to newly created file: ' + command_path_str)
            self.write_file(command_path_str, line)
            self.set_permission(command_path_str, "755")

            self.logger.debug('Command created successfully ' + command_path)

            self.logger.debug('Adding command to command_path_list')
            command_path_list.append(command_path)

            return 0, p_out, p_err
        else:
            self.logger.debug('Wrap could not created ' + command_path)
            return 1, p_out, p_err

    def add_resource_limits(self, command_path, polkit_status, cpu, memory):
        self.logger.debug('Adding resource limits to wrapper command.')
        lines = ''
        if cpu and memory is not None:
            self.logger.debug('Adding both CPU and memory limits.')
            lines = 'ulimit -Sv ' + str(memory) + '\n'
            lines += 'COMMAND=\"' + str(command_path) + '-ahenk $@\"\n'
            lines += 'nohup pkexec --user $USER $COMMAND &\n'
            lines += 'U_PID=$!\n'
            lines += 'cpulimit -p $U_PID -l ' + str(cpu) + ' -z\n'
        elif cpu is not None:
            self.logger.debug('Adding only CPU limit.')
            lines = 'COMMAND=\"' + str(command_path) + '-ahenk $@\"\n'
            lines += 'nohup pkexec --user $USER $COMMAND &\n'
            lines += 'U_PID=$!\n'
            lines += 'cpulimit -p $U_PID -l ' + str(cpu) + ' -z\n'
        elif memory is not None:
            self.logger.debug('Adding only memory limit.')
            lines = 'ulimit -Sv ' + str(memory) + '\n'
            lines += 'COMMAND=\"' + str(command_path) + '-ahenk $@\"\n'
            lines += 'nohup pkexec --user $USER $COMMAND &\n'

        return lines

    def create_logout_files(self, username, path_of_plugin, add_user_list, del_user_list, command_path_list):
        path_of_changes = path_of_plugin + 'user-privilege/privilege.changes'
        if not os.path.exists(path_of_changes):
            self.create_directory(path_of_changes)

        self.logger.debug('Creating JSON data for user privilege changes.')
        data = {'added_user_list': add_user_list, 'deleted_user_list': del_user_list,
                'command_path_list': command_path_list}

        path_of_user_changes = path_of_changes + '/' + username + '.changes'
        self.logger.debug('Creating file: ' + path_of_user_changes)
        with open(path_of_user_changes, 'w') as f:
            self.logger.debug('Writing JSON data to: ' + path_of_user_changes)
            json.dump(data, f)


def handle_policy(profile_data, context):
    user_privilege = UserPrivilege(profile_data, context)
    user_privilege.handle_policy()
