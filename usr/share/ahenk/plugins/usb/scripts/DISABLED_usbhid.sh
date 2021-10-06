#!/bin/bash

var=$(lsmod | grep usbhid)

if [[ -z "$var" ]]
then
echo "USB HID devices are already blocked"
else
for device in /sys/bus/usb/drivers/usbhid/* ; do
       if [[ $device == *:* ]]
       then
               echo "${device##*/}"
               echo "${device##*/}" | tee -a /sys/bus/usb/drivers/usbhid/unbind
       fi
done

sleep 2
rmmod usbhid
echo blacklist usbhid >> /etc/modprobe.d/blockusbhid.conf
fi

var=$(lsmod | grep psmouse)

if [[ -z "$var" ]]
then
echo "psmouse is already blocked"
else
rmmod psmouse
echo blacklist psmouse >> /etc/modprobe.d/blockusbhid.conf
fi

#for ld in `who | grep $1 | egrep -o " \(:[0-9]+\)" | egrep -o ":[0-9]+"`; do
# export DISPLAY="$ld"
# for hid in `sudo -u $1 xinput --list | grep slave | grep -o 'id=[0-9]\+' | grep -o '[0-9]\+'`; do
 #    sudo -u $1 xinput set-int-prop $hid "Device Enabled" 8 0
 #done
#done
