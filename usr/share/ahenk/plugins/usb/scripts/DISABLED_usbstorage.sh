#!/bin/bash

var=$(lsmod | awk '{print $1}'| grep usb_storage)

if [[ -z "$var" ]]
then
echo "USB storage devices are already blocked"
else
rm /etc/modprobe.d/blockusbstorages.conf
for device in /sys/bus/usb/drivers/usb-storage/* ; do
       if [[ $device == *:* ]]
       then
               echo "${device##*/}"
               echo "${device##*/}" | tee -a /sys/bus/usb/drivers/usb-storage/unbind
       fi
done

sleep 2

for usb_dev in /dev/disk/by-id/usb-*; do
    dev=$(readlink -f $usb_dev)
    grep -q ^$dev /proc/mounts && umount -f $dev 
done

sleep 2

var=$(lsmod | grep usb_storage | awk '{print $4}')

if [[ ! -z "$var" ]]
then
IFS=',' read -ra deps <<< "$var"
for i in "${deps[@]}"; do
	modprobe -r "$i"
    echo blacklist "$i" >> /etc/modprobe.d/blockusbstorages.conf
done
fi

sleep 2

modprobe -r usb_storage
echo blacklist usb_storage >> /etc/modprobe.d/blockusbstorages.conf
sleep 2
fi



