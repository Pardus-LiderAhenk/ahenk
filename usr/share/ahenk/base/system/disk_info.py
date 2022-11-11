#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Agah Hulusi ÖZ <enghulusi@gmail.com>

from base.util.util import Util

# HDD and SSD disk information
class DiskInfo():

    @staticmethod
    def get_all_disks():
        result_code, p_out, p_err = Util.execute("lsblk -b -o NAME,TYPE,ROTA,SIZE,RM,HOTPLUG,FSUSED | grep -v loop | awk '$5 == \"0\" { print $0 }'")
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
                if len(item) > 6 and item[0] != "NAME":
                    used += int(item[6])
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