#!/bin/bash

modprobe usbhid
modprobe psmouse


#for ld in `who | grep $1 | egrep -o " \(:[0-9]+\)" | egrep -o ":[0-9]+"`; do
# export DISPLAY="$ld"
# for hid in `sudo -u $1 xinput --list | grep slave | grep -o 'id=[0-9]\+' | grep -o '[0-9]\+'`; do
#     sudo -u $1 xinput set-int-prop $hid "Device Enabled" 8 1
# done
#done

echo "" > /etc/modprobe.d/blockusbhid.conf
