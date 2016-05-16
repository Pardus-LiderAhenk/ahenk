#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import platform
import psutil
from uuid import getnode as get_mac


class System:
    class Process(object):

        @staticmethod
        def pids():
            return psutil.pids()

        @staticmethod
        def find_pid_by_name(p_name):
            for id in psutil.pids():
                if psutil.Process(id).name() == p_name:
                    return id
            return None

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

    class Os(object):

        @staticmethod
        def boot_time():
            return psutil.boot_time()

        @staticmethod
        def architecture():
            return platform.architecture()[0]

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

        @staticmethod
        def mac_address():
            return str(':'.join(("%012X" % get_mac())[i:i + 2] for i in range(0, 12, 2)))

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
                return int(int(psutil.disk_usage('/')[0]) / (1024 * 1024))

            @staticmethod
            def used():
                return int(int(psutil.disk_usage('/')[1]) / (1024 * 1024))

            @staticmethod
            def free():
                return int(int(psutil.disk_usage('/')[2]) / (1024 * 1024))

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
            def interfaces_details():
                return psutil.net_if_addrs()

            @staticmethod
            def io_counter_detail():
                return psutil.net_io_counters(pernic=True)

            @staticmethod
            def interfaces():
                arr = []
                for iface in psutil.net_if_addrs():
                    arr.append(str(iface))
                return arr

            @staticmethod
            def ip_addresses():
                arr = []
                for iface in psutil.net_io_counters(pernic=True):
                    arr.append(psutil.net_if_addrs()[str(iface)][0][1])
                return arr

        class Cpu(object):

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
            def times():
                return psutil.cpu_times()

            @staticmethod
            def architecture():
                return platform.processor()
