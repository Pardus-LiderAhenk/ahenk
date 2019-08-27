#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime
import grp
import hashlib
import json
import os
import pwd
import shutil
import stat
import subprocess
import uuid
import locale
from base.scope import Scope


class Util:


    def __init__(self):
        super().__init__()

    @staticmethod
    def get_ask_path_file():
        return '/usr/share/ahenk/base/agreement/'

    @staticmethod
    def close_session(username):
        Util.execute('pkill -9 -u {0}'.format(username))

    @staticmethod
    def shutdown():
        Util.execute('reboot')

    @staticmethod
    def create_file(full_path):
        try:
            if os.path.exists(full_path):
                return None
            else:
                file = open(full_path, 'w')
                file.close()
                return True
        except:
            raise

    @staticmethod
    def delete_folder(full_path):
        try:
            shutil.rmtree(full_path)
        except:
            raise

    @staticmethod
    def delete_file(full_path):
        try:
            if Util.is_exist(full_path):
                os.remove(full_path)
        except:
            raise

    @staticmethod
    def rename_file(old_full_path, new_full_path):
        try:
            os.rename(old_full_path, new_full_path)
        except:
            raise

    @staticmethod
    def copy_file(source_full_path, destination_full_path):
        try:
            shutil.copy2(source_full_path, destination_full_path)
        except:
            raise

    @staticmethod
    def move(source_full_path, destination_full_path):
        try:
            shutil.move(source_full_path, destination_full_path)
        except:
            raise

    @staticmethod
    def get_size(full_path):
        # byte
        try:
            return os.path.getsize(full_path)
        except:
            raise

    @staticmethod
    def link_path(source_path, destination_path):
        try:
            os.symlink(source_path, destination_path)
        except:
            raise

    @staticmethod
    def read_file(full_path, mode='r'):
        content = None
        try:
            with open(full_path, mode) as f:
                content = f.read()
        except:
            raise
        finally:
            return content

    @staticmethod
    def read_file_by_line(full_path, mode='r'):
        line_list = list()
        with open(full_path, mode) as f:
            lines = f.readlines()
            for line in lines:
                line_list.append(line)
        return line_list

    @staticmethod
    def write_file(full_path, content, mode='w+'):
        file = None
        try:
            file = open(full_path, mode)
            file.write(content)
        except:
            raise
        finally:
            file.close()

    @staticmethod
    def make_executable(full_path):
        try:
            st = os.stat(full_path)
            os.chmod(full_path, st.st_mode | stat.S_IEXEC)
        except:
            raise

    @staticmethod
    def change_owner(full_path, user_name=None, group_name=None):
        try:
            shutil.chown(full_path, user_name, group_name)
        except:
            raise

    @staticmethod
    def execute(command, stdin=None, env=None, cwd=None, shell=True, result=True, as_user=None, ip=None):

        try:
            if ip:
                command = 'ssh root@{0} "{1}"'.format(ip, command)
                Scope.get_instance().get_logger().debug('Executing command: ' +str(command))

            elif as_user:
                command = 'su - {0} -c "{1}"'.format(as_user, command)
                Scope.get_instance().get_logger().debug('Executing command: ' +str(command))
            process = subprocess.Popen(command, stdin=stdin, env=env, cwd=cwd, stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE, shell=shell)

            Scope.get_instance().get_logger().debug('Executing command: ' + str(command))

            if result is True:
                result_code = process.wait()
                p_out = process.stdout.read().decode("unicode_escape")
                p_err = process.stderr.read().decode("unicode_escape")

                return result_code, p_out, p_err
            else:
                return None, None, None
        except Exception as e:
            return 1, 'Could not execute command: {0}. Error Message: {1}'.format(command, str(e)), ''

    @staticmethod
    def scopy_from_remote(source_path, destination_path, ip):
        command = 'scp -r root@' + ip + ':' + source_path + ' ' + destination_path
        process = subprocess.Popen(command,  stderr=subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
        result_code = process.wait()
        p_out = process.stdout.read().decode("unicode_escape")
        p_err = process.stderr.read().decode("unicode_escape")

        return result_code, p_out, p_err

    @staticmethod
    def execute_script(script_path, parameters=None):
        command = []
        if os.path.exists(script_path):
            command.append(script_path)
        else:
            raise Exception('[Util] Script is required')
        if parameters is not None:    
            for p in parameters:
                command.append(p)

        return subprocess.check_call(command)

    @staticmethod
    def is_exist(full_path):
        try:
            return os.path.exists(full_path)
        except:
            raise

    @staticmethod
    def create_directory(dir_path):
        try:
            return os.makedirs(dir_path)
        except:
            raise

    @staticmethod
    def string_to_json(string):
        try:
            return json.loads(string)
        except:
            raise

    # TODO json abilities


    @staticmethod
    def file_owner(full_path):
        try:
            st = os.stat(full_path)
            uid = st.st_uid
            return pwd.getpwuid(uid)[0]
        except:
            raise

    @staticmethod
    def file_group(full_path):
        try:
            st = os.stat(full_path)
            gid = st.st_gid
            # return grp.getgrgid(gid)[0]
            return gid
        except:
            raise

    @staticmethod
    def install_with_dpkg(full_path):
        command_dpkg = 'dpkg -i {0}'
        command_dep = 'apt -f install -y'
        commands = [command_dpkg.format(full_path),command_dep]
        for cmd in commands:
            try:
                process = subprocess.Popen(cmd, shell=True)
                process.wait()
            except:
                raise

    @staticmethod
    def install_with_apt_get(package_name, package_version=None):

        if package_version is not None:
            command = 'apt-get install --yes --force-yes {0}={1}'.format(package_name, package_version)
        else:
            command = 'apt-get install --yes --force-yes {0}'.format(package_name)

        return Util.execute(command)

    @staticmethod
    def uninstall_package(package_name, package_version=None):

        if package_version is not None:
            command = 'apt-get purge --yes --force-yes {0}={1}'.format(package_name, package_version)
        else:
            command = 'apt-get purge --yes --force-yes {0}'.format(package_name)

        return Util.execute(command)

    @staticmethod
    def is_installed(package_name):

        result_code, p_out, p_err = Util.execute('dpkg -s {0}'.format(package_name))
        try:
            lines = str(p_out).split('\n')
            for line in lines:
                if len(line) > 1:
                    if line.split(None, 1)[0].lower() == 'status:':
                        if 'installed' in line.split(None, 1)[1].lower():
                            return True
            return False
        except Exception as e:
            return False

    @staticmethod
    def get_md5_file(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return str(hash_md5.hexdigest())

    @staticmethod
    def get_md5_text(content):
        hash_md5 = hashlib.md5()
        hash_md5.update(content.encode())
        return str(hash_md5.hexdigest())

    @staticmethod
    def timestamp():
        return str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def get_language():
        locale_info = locale.getdefaultlocale()
        return locale_info[0]

    @staticmethod
    def set_permission(path, permission_code):
        Util.execute('chmod -R {0} {1}'.format(permission_code, path))

    @staticmethod
    def has_attr_json(arg, attr_name):
        for j in json.loads(json.dumps(arg)):
            if attr_name in j:
                return True
        return False

    @staticmethod
    def remove_package(package_name, package_version):
        command = "sudo apt-get --yes --force-yes purge {0}={1}".format(package_name, package_version)
        result_code, p_out, p_err = Util.execute(command)
        return result_code, p_out, p_err

    @staticmethod
    def send_notify(title, body, display, user, icon=None, timeout=5000):

        inner_command = 'notify-send "{0}" "{1}" -t {2}'.format(title, body, timeout)
        if icon:
            inner_command += ' -i {0}'.format(icon)

        if user != 'root':
            Util.execute('export DISPLAY={0}; su - {1} -c \'{2}\''.format(display, user, inner_command))

    @staticmethod
    def show_message(username,display=':0',message='', title=''):
        ask_path = Util.get_ask_path_file()+ 'confirm.py'
        try:

            if username is not None:
                command = 'export DISPLAY={0};su - {1} -c \'python3 {2} \"{3}\" \"{4}\"\''.format(display, username,
                                                                                                  ask_path,
                                                                                                  message,
                                                                                                  title)
                result_code, p_out, p_err = Util.execute(command)

                if p_out.strip() == 'Y':
                    return True
                elif p_out.strip() == 'N':
                    return False
                else:
                    return None

            else:
                return None
        except Exception as e :
            print("Error when showing message " + str(e))

            return None;



    @staticmethod
    def show_registration_message(login_user_name,message,title,host=None):

        ask_path = Util.get_ask_path_file()+ 'ahenkmessage.py'

        display_number = ":0"

        if host is None:
            command = 'export DISPLAY={0}; su - {1} -c \"python3 {2} \'{3}\' \'{4}\' \"'.format(display_number, login_user_name,
                                                                                        ask_path, message, title)
        else:
            command = 'export DISPLAY={0}; su - {1} -c \"python3 {2} \'{3}\' \'{4}\' \'{5}\' \"'.format(display_number,
                                                                                                        login_user_name,
                                                                                                        ask_path,
                                                                                                        message, title,
                                                                                                        host)
        result_code, p_out, p_err = Util.execute(command)

        pout = str(p_out).replace('\n', '')

        return pout

    @staticmethod
    def show_unregistration_message(login_user_name,display_number,message,title):

        ask_path = Util.get_ask_path_file()+ 'unregistrationmessage.py'

        command = 'export DISPLAY={0}; su - {1} -c \"python3 {2} \'{3}\' \'{4}\' \"'.format(display_number,
                                                                                                        login_user_name,
                                                                                                        ask_path,
                                                                                                        message, title
                                                                                                        )
        result_code, p_out, p_err = Util.execute(command)

        pout = str(p_out).replace('\n', '')

        return pout

