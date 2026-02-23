#!/bin/bash

# Default file name for policy
DEFAULT_FILE_NAME="99-block-hid.rules"

# file nane for task
FILE_NAME="${1:-$DEFAULT_FILE_NAME}"

rm -f /etc/udev/rules.d/$FILE_NAME
udevadm control --reload-rules

for device in /sys/bus/usb/devices/*; do
    if [ -e "$device/authorized" ]; then
        status=$(cat "$device/authorized")
        if [ "$status" == "0" ]; then
            echo 1 > "$device/authorized" 2>/dev/null
        fi
    fi
done

udevadm trigger --subsystem-match=usb
udevadm trigger --action=add