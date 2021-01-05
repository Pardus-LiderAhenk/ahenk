#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import configparser
import fcntl
import glob
import os
import platform
import re
import socket
import struct
import netifaces
from uuid import getnode as get_mac

import cpuinfo
import psutil

from base.scope import Scope
from base.util.util import Util


class System:
    def __init__(self):
        scope = Scope().get_instance()
        self.db_service = scope.get_db_service()
        self.logger = scope.get_logger()

    class BIOS(object):
        @staticmethod
        def vendor():
            try:
                result_code, p_out, p_err = Util.execute('dmidecode --string bios-vendor')
                return int(result_code), str(p_out), str(p_err)
            except:
                raise

        @staticmethod
        def release_date():
            try:
                result_code, p_out, p_err = Util.execute('dmidecode --string bios-release-date')
                return int(result_code), str(p_out), str(p_err)
            except:
                raise

        @staticmethod
        def version():
            try:
                result_code, p_out, p_err = Util.execute('dmidecode --string bios-version')
                return int(result_code), str(p_out), str(p_err)
            except:
                raise

    class Ahenk(object):

        @staticmethod
        def installed_plugins():
            plugin_names = []
            possible_plugins = os.listdir(System.Ahenk.plugins_path())
            for plugin_name in possible_plugins:
                location = os.path.join(System.Ahenk.plugins_path(), plugin_name)
                if os.path.isdir(location) and System.Ahenk.module_name() + ".py" in os.listdir(location):
                    plugin_names.append(plugin_name)
            return plugin_names

        @staticmethod
        def db_path():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('BASE', 'dbPath')

        @staticmethod
        def agreement_timeout():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('SESSION', 'agreement_timeout')

        @staticmethod
        def registration_timeout():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('SESSION', 'registration_timeout')

        @staticmethod
        def get_policy_timeout():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('SESSION', 'get_policy_timeout')

        @staticmethod
        def uid():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('CONNECTION', 'uid')

        @staticmethod
        def plugins_path():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('PLUGIN', 'pluginfolderpath')

        @staticmethod
        def module_name():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('PLUGIN', 'mainModuleName')

        @staticmethod
        def agreement():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('MACHINE', 'agreement')

        @staticmethod
        def dn():
            system = System()
            try:
                dn = system.db_service.select_one_result('registration', 'dn', " registered='1'")
                return dn
            except:
                return None

        @staticmethod
        def ip():
            system = System()
            try:
                ip = system.db_service.select_one_result('session', 'ip')
                return ip
            except:
                return None

        @staticmethod
        def get_pid_number():
            pid_number = None
            try:
                if os.path.exists(System.Ahenk.pid_path()):
                    file = open(System.Ahenk.pid_path(), 'r')
                    pid_number = file.read()
                    file.close()
                return pid_number
            except Exception as e:
                return None

        @staticmethod
        def is_running():
            try:
                if System.Ahenk.get_pid_number() is not None:
                    return psutil.pid_exists(int(System.Ahenk.get_pid_number()))
                else:
                    return False
            except Exception as e:
                return False

        @staticmethod
        def config_path():
            return '/etc/ahenk/ahenk.conf'

        @staticmethod
        def pid_path():
            return '/var/run/ahenk.pid'

        @staticmethod
        def fifo_file():
            return '/tmp/liderahenk.fifo'

        @staticmethod
        def received_dir_path():
            path = '/tmp/' # move this to properties
            if Util.is_exist(path) is False:
                Util.create_directory(path)
                Util.set_permission(path, '777')
            return path

    class Process(object):

        @staticmethod
        def process_by_pid(pid):
            return psutil.Process(pid)

        @staticmethod
        def pids():
            return psutil.pids()

        @staticmethod
        def find_pids_by_name(p_name):
            arr = []
            for pid in psutil.pids():
                if psutil.Process(id).name() == p_name:
                    arr.append(pid)
            return arr

        @staticmethod
        def is_running(pid):
            return psutil.pid_exists(pid)

        @staticmethod
        def kill_by_pid(pid):
            return psutil.Process(pid).kill()

        @staticmethod
        def kill_by_pids(pids):
            for pid in pids:
                psutil.Process(pid).kill()

        @staticmethod
        def find_name_by_pid(pid):
            return psutil.Process(pid).name()

        @staticmethod
        def path(pid):
            return psutil.Process(pid).exe()

        @staticmethod
        def working_directory(pid):
            return psutil.Process(pid).cwd()

        @staticmethod
        def command_line(pid):
            return psutil.Process(pid).cmdline()

        @staticmethod
        def status(pid):
            return psutil.Process(pid).status()

        @staticmethod
        def username(pid):
            return psutil.Process(pid).username()

        @staticmethod
        def create_time(pid):
            return psutil.Process(pid).create_time()

        @staticmethod
        def cpu_times(pid):
            return psutil.Process(pid).cpu_times()

        @staticmethod
        def cpu_percent(pid):
            return psutil.Process(pid).cpu_percent(interval=1.0)

        @staticmethod
        def memory_percent(pid):
            return psutil.Process(pid).memory_percent()

        @staticmethod
        def open_files(pid):
            return psutil.Process(pid).open_files()

        @staticmethod
        def connections(pid):
            return psutil.Process(pid).connections()

        @staticmethod
        def threads(pid):
            return psutil.Process(pid).threads()

        @staticmethod
        def nice(pid):
            return psutil.Process(pid).nice()

        @staticmethod
        def environment(pid):
            return psutil.Process(pid).environ()

        @staticmethod
        def details():
            return psutil.test()

    class Sessions(object):

        @staticmethod
        def user_name():
            arr = []
            for user in psutil.users():
                if str(user[0]) is not 'None' and user[0] not in arr:
                    arr.append(user[0])
            return arr

        @staticmethod
        def user_details():
            return psutil.users()

        @staticmethod
        def display(username):
            system = System()
            if "\\" in username:
                user_parser = username.split("\\")
                username = user_parser[1]
            display = system.db_service.select_one_result('session', 'display', " username='{0}'".format(username))
            return display

        @staticmethod
        def desktop(username):
            system = System()
            desktop = system.db_service.select_one_result('session', 'desktop', " username='{0}'".format(username))
            return desktop

        @staticmethod
        def userip(username):
            system = System()
            if "\\" in username:
                user_parser = username.split("\\")
                username = user_parser[1]
            userip = system.db_service.select_one_result('session', 'ip', " username='{0}'".format(username))
            return userip

        @staticmethod
        def user_home_path(username):
            # TODO temp
            return '/home/{0}/'.format(str(username))

    class Os(object):

        @staticmethod
        def architecture():
            return platform.architecture()[0]

        @staticmethod
        def boot_time():
            return psutil.boot_time()

        @staticmethod
        def file_format():
            return platform.architecture()[1]

        @staticmethod
        def name():
            return platform.system()

        @staticmethod
        def distribution_name():
            return platform.linux_distribution()[0]

        @staticmethod
        def distribution_version():
            return platform.linux_distribution()[1]

        @staticmethod
        def distribution_id():
            return platform.linux_distribution()[2]

        @staticmethod
        def version():
            return platform.version()

        @staticmethod
        def kernel_release():
            return platform.release()

        @staticmethod
        def hostname():
            return platform.node()

    class Hardware(object):

        class BaseBoard(object):

            @staticmethod
            def manufacturer():
                try:
                    result_code, p_out, p_err = Util.execute('dmidecode --string baseboard-manufacturer')
                    return int(result_code), str(p_out), str(p_err)
                except:
                    raise

            @staticmethod
            def product_name():
                try:
                    result_code, p_out, p_err = Util.execute('dmidecode --string baseboard-product-name')
                    return int(result_code), str(p_out), str(p_err)
                except:
                    raise

            @staticmethod
            def version():
                try:
                    result_code, p_out, p_err = Util.execute('dmidecode --string baseboard-version')
                    return int(result_code), str(p_out), str(p_err)
                except:
                    raise

            @staticmethod
            def serial_number():
                try:
                    result_code, p_out, p_err = Util.execute('dmidecode --string baseboard-serial-number')
                    return int(result_code), str(p_out), str(p_err)
                except:
                    raise

            @staticmethod
            def asset_tag():
                try:
                    result_code, p_out, p_err = Util.execute('dmidecode --string baseboard-asset-tag')
                    return int(result_code), str(p_out), str(p_err)
                except:
                    raise

        class Memory(object):

            @staticmethod
            def total():
                return int(int(psutil.virtual_memory()[0]) / (1024 * 1024))

            @staticmethod
            def available():
                return int(int(psutil.virtual_memory()[1]) / (1024 * 1024))

            @staticmethod
            def percent():
                return psutil.virtual_memory()[2]

            @staticmethod
            def used():
                return int(int(psutil.virtual_memory()[3]) / (1024 * 1024))

            @staticmethod
            def free():
                return int(int(psutil.virtual_memory()[4]) / (1024 * 1024))

        class Disk(object):

            @staticmethod
            def total():
                return int(int(psutil.disk_usage('/')[0]) / (1000 * 1000))

            @staticmethod
            def used():
                return int(int(psutil.disk_usage('/')[1]) / (1000 * 1000))

            @staticmethod
            def free():
                return int(int(psutil.disk_usage('/')[2]) / (1000 * 1000))

            @staticmethod
            def percent():
                return psutil.disk_usage('/')[3]

            @staticmethod
            def partitions():
                return psutil.disk_partitions()

        class Network(object):

            @staticmethod
            def interface_size():
                return len(psutil.net_io_counters(pernic=True))

            @staticmethod
            def io_counter_detail():
                return psutil.net_io_counters(pernic=True)

            @staticmethod
            def interfaces():
                arr = []
                for iface in psutil.net_io_counters(pernic=True):
                    arr.append(str(iface))
                return arr

            @staticmethod
            def ip_addresses():
                arr = []
                for iface in netifaces.interfaces():
                    link = None
                    try:
                        link = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
                    except:
                        link = None
                    if link is not None:
                        ip = link['addr']
                        if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$',
                                ip) and str(ip) != 'localhost' and str(ip) != '127.0.0.1':
                            arr.append(ip)
                return arr

            @staticmethod
            def getHwAddr(ifname):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
                return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

            @staticmethod
            def getHwAddr(ifname):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
                return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

            @staticmethod
            def mac_addresses():
                mac = get_mac()
                ':'.join(("%012X" % mac)[i:i + 2] for i in range(0, 12, 2))
                arr = []
                for iface in psutil.net_io_counters(pernic=True):
                    try:
                        addr_list = psutil.net_if_addrs()
                        mac = addr_list[str(iface)][2][1]
                        if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()) and str(
                                mac) != '00:00:00:00:00:00':
                            arr.append(mac.lower())
                    except Exception as e:
                        pass

                return arr

        @staticmethod
        def screen_info_json_obj(info):
            label_list = [
                # 'Identifier',
                          'ModelName', 'VendorName', 'Monitor Manufactured', 'DisplaySize',
                          # 'Gamma',
                          # 'Horizsync',
                          # 'VertRefresh'
                          ]
            data = dict()

            for line in info.splitlines():
                line = line.strip().replace('"', '')
                intersection = list(set(line.split(' ')).intersection(label_list))
                if len(intersection) > 0:
                    data[str(intersection[0])] = line.split(intersection[0])[1].strip()

            return data

        @staticmethod
        def monitors():
            edid_list = glob.glob('/sys/class/drm/*/edid')

            monitor_list = list()
            for edid in edid_list:
                result_code, p_out, p_err = Util.execute('parse-edid < {0}'.format(edid))

                if result_code == 0:
                    monitor_list.append(System.Hardware.screen_info_json_obj(p_out))

            return monitor_list

        @staticmethod
        def screens():
            result_code, p_out, p_err = Util.execute('xrandr')
            arr = []
            if result_code == 0:
                for line in p_out.splitlines():
                    if len(list(set(line.split(' ')).intersection(['connected']))) > 0:
                        arr.append(line)
            return arr

        @staticmethod
        def usb_devices():
            result_code, p_out, p_err = Util.execute('lsusb')
            arr = []
            if result_code == 0:
                for line in p_out.splitlines():
                    if ':' in line and 'Device 001' not in line.split(':')[0]:
                        arr.append(line)
            return arr

        @staticmethod
        def printers():
            result_code, p_out, p_err = Util.execute('lpstat -a')
            arr = None
            if result_code == 0:
                arr = p_out.splitlines()
            return arr

        @staticmethod
        def system_definitions():
            result_code, p_out, p_err = Util.execute('dmidecode -t system')
            arr = []
            if result_code == 0:
                for line in p_out.splitlines():
                    line = line.strip()
                    if len(list(set(line.split(' ')).intersection(['Manufacturer:', 'Product']))) > 0:
                        arr.append(line)
            return arr

        @staticmethod
        def machine_model():
            try:
                result_code, p_out, p_err = Util.execute('sudo dmidecode --string system-version')
                return str(p_out)
            except:
                raise

        @staticmethod
        def machine_type():
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            return config.get('MACHINE', 'type')

        @staticmethod
        def interfaces_details():
            return psutil.net_if_addrs()

        @staticmethod
        def ip_addresses():
            arr = []
            for iface in psutil.net_io_counters(pernic=True):
                ip = psutil.net_if_addrs()[str(iface)][0][1]
                if re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', ip) and str(
                        ip) != 'localhost' and str(ip) != '127.0.0.1':
                    arr.append(ip)
            return arr

        class Cpu(object):

            @staticmethod
            def times():
                return psutil.cpu_times()

            @staticmethod
            def architecture():
                return platform.processor()

            @staticmethod
            def physical_core_count():
                return psutil.cpu_count(logical=False)

            @staticmethod
            def logical_core_count():
                return psutil.cpu_count(logical=True)

            @staticmethod
            def stats():
                return psutil.cpu_stats()

            @staticmethod
            def vendor():
                return cpuinfo.get_cpu_info()['vendor_id']

            @staticmethod
            def brand():
                return cpuinfo.get_cpu_info()['brand']

            @staticmethod
            def hz_advertised():
                return cpuinfo.get_cpu_info()['hz_advertised']

            @staticmethod
            def hz_actual():
                return cpuinfo.get_cpu_info()['hz_actual']

            @staticmethod
            def bit():
                return cpuinfo.get_cpu_info()['bits']

            @staticmethod
            def family():
                return cpuinfo.get_cpu_info()['family']

            @staticmethod
            def model():
                return cpuinfo.get_cpu_info()['model']
