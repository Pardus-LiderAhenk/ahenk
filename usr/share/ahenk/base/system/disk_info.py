# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Agah Hulusi ÖZ <enghulusi@gmail.com>

from base.util.util import Util
import psutil

# HDD and SSD disk information
class DiskInfo():

    @staticmethod
    def total_disk_used():
        ssd_list, hdd_list = DiskInfo.get_all_disks()
        total_disk_usage = 0
        if len(ssd_list) > 0:
            for disk in ssd_list:
                total_disk_usage += int(disk['used'])
        if len(hdd_list) > 0:
            for disk in hdd_list:
                total_disk_usage += int(disk['used'])
        return total_disk_usage

    @staticmethod
    def total_disk():
        ssd_list, hdd_list = DiskInfo.get_all_disks()
        total_size = 0
        for disk in ssd_list:
            total_size += int(disk['total'])
        for disk in hdd_list:
            total_size += int(disk['total'])
        return total_size

    @staticmethod
    def total_disk_free():
        ssd_list, hdd_list = DiskInfo.get_all_disks()
        total_disk_free = 0
        if len(ssd_list) > 0:
            for disk in ssd_list:
                total_disk_free += int(disk['total']) - int(disk['used'])
        if len(hdd_list) > 0:
            for disk in hdd_list:
                total_disk_free += int(disk['total']) - int(disk['used'])
        return total_disk_free

    @staticmethod
    def get_all_disks():
        result_code, p_out, p_err = Util.execute("lsblk -b -o NAME,TYPE,ROTA,SIZE,RM,HOTPLUG,MOUNTPOINT,FSUSED | grep -v loop | awk '$5 == \"0\" { print $0 }'")
        txt = p_out.split("\n")
        while '' in txt:
            txt.remove('')
        detail_txt = []
        ssd_list = []
        hdd_list = []
        # Ignore USB from list
        for item in txt:
            item = item.split()
            detail_txt.append(item)
        # SSD and HDD list
        for disk in detail_txt:
            # Second element of disk equal to rotation type.
            # Rotation type show that disk is SSD or HDD
            # If it equals to "0" SSD
            # If it equals to "1" HDD
            if disk[2] == "0" and disk[1] == "disk":
                ssd_list.append({
                    "name": disk[0],
                    "type": "SSD",
                    "total": disk[3],
                    "used": 0,
                })
            elif disk[2] == "1" and disk[1] == "disk":
                hdd_list.append({
                    "name": disk[0],
                    "type": "HDD",
                    "total": disk[3],
                    "used": 0,
                })
        # Calculate the usage
        used = 0
        ssd_list_counter = 0
        hdd_list_counter = 0
        is_first_disk = True
        resource_name = 0
        resource_disk = 0
        for item in detail_txt:
            if item[1] == "disk":
                if is_first_disk:
                    total = item[3]
                    name = item[0]
                    type = item[2]
                    is_first_disk = False
                else:
                    if type == "0":
                        ssd_list[ssd_list_counter]["used"] = used
                        ssd_list_counter += 1
                    elif type == "1":
                        hdd_list[hdd_list_counter]["used"] = used
                        hdd_list_counter += 1
                    name = item[0]
                    used = 0
                    total = item[3]
                    type = item[2]
            else:
                if len(item) > 7 and item[0] != "NAME":
                    if item[6] == "/":
                        resource_disk = psutil.disk_usage(item[6])[0]
                        resource_name = name
                    used += int(item[7])
        for i in ssd_list:
            if i["name"] == resource_name:
                i["total"] = resource_disk
        for i in hdd_list:
            if i["name"] == resource_name:
                i["total"] = resource_disk
        if type == "0":
            ssd_list[ssd_list_counter]["used"] = used
            ssd_list_counter += 1
        elif type == "1":
            hdd_list[hdd_list_counter]["used"] = used
            hdd_list_counter += 1
        for item in ssd_list:
            item["total"]= int(int(item["total"]) / (1000 * 1000))
            item["used"] = int(int(item["used"]) / (1000 * 1000))
        for item in hdd_list:
            item["total"] = int(int(item["total"]) / (1000 * 1000))
            item["used"] = int(int(item["used"]) / (1000 * 1000))
        return ssd_list, hdd_list
