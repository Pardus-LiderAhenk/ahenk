#!/bin/bash

while read line           
do           
	IFS=' ' read -a module <<< "$line"
    modprobe "${module[1]}"           
done < /etc/modprobe.d/blockusbstorages.conf

echo "" | tee -a /etc/modprobe.d/blockusbstorages.conf

modprobe usb_storage

for usb_dev in /dev/disk/by-id/usb-*; do
    dev=$(readlink -f $usb_dev)
    grep -q ^$dev /proc/mounts && mount -f $dev 
done